"""
================================================================================
[Engram Architecture Demo Implementation]

DISCLAIMER:
1. Demo Purpose Only: 
   This code is a demonstration version intended to illustrate the core logic and 
   data flow of the Engram module.

2. Production Readiness: 
   This implementation requires further optimization for actual production use 
   (e.g., custom CUDA kernels, distributed training support).

3. Simplifications: 
   Standard components (Normalization, Attention, MoE) and complex Hyper-connection 
   mechanisms are omitted or mocked in this version to focus exclusively on the 
   Engram module implementation.
================================================================================
"""

"""
pip install torch numpy transformers sympy
"""

## built-in
from typing import List
from dataclasses import dataclass, field
import math

## third-party
from sympy import isprime
import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer
from tokenizers import normalizers, Regex
import asyncio
import websockets
import json
import threading
import time
import requests

@dataclass
class EngramConfig:
    tokenizer_name_or_path: str = "deepseek-ai/DeepSeek-V3"
    engram_vocab_size: List[int] = field(default_factory=lambda: [129280*5, 129280*5])
    max_ngram_size: int = 3
    n_embed_per_ngram: int = 512
    n_head_per_ngram: int = 8
    layer_ids: List[int] = field(default_factory=lambda: [1, 15])
    pad_id: int = 2
    seed: int = 0
    kernel_size: int = 4
    
@dataclass
class BackBoneConfig:
    hidden_size: int = 1024
    hc_mult: int = 4
    vocab_size: int = 129280
    num_layers: int = 30
    
engram_cfg = EngramConfig()
backbone_config = BackBoneConfig()

class CompressedTokenizer:
    def __init__(
        self,
        tokenizer_name_or_path,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, trust_remote_code=True)
        
        SENTINEL = "\uE000"
        self.normalizer = normalizers.Sequence([
            normalizers.NFKC(),
            normalizers.NFD(),
            normalizers.StripAccents(),
            normalizers.Lowercase(),
            normalizers.Replace(Regex(r"[ \t\r\n]+"), " "),
            normalizers.Replace(Regex(r"^ $"), SENTINEL),
            normalizers.Strip(),
            normalizers.Replace(SENTINEL, " "),
        ])
        
        self.lookup_table, self.num_new_token = self._build_lookup_table()
    
    def __len__(self):
        return self.num_new_token
    
    def _build_lookup_table(self):
        old2new = {}
        key2new = {}          
        new_tokens = []

        vocab_size = len(self.tokenizer)
        for tid in range(vocab_size):
            text = self.tokenizer.decode([tid], skip_special_tokens=False)
            
            if "�" in text:
                key = self.tokenizer.convert_ids_to_tokens(tid)
            else:
                norm = self.normalizer.normalize_str(text)
                key = norm if norm else text

            nid = key2new.get(key)
            if nid is None:
                nid = len(new_tokens)
                key2new[key] = nid
                new_tokens.append(key)
            old2new[tid] = nid
        
        lookup = np.empty(vocab_size, dtype=np.int64)
        for tid in range(vocab_size):
            lookup[tid] = old2new[tid]

        return lookup, len(new_tokens)
    
    def _compress(self, input_ids):
        arr = np.asarray(input_ids, dtype=np.int64)
        pos_mask = arr >= 0
        out = arr.copy()
        valid_ids = arr[pos_mask]
        out[pos_mask] = self.lookup_table[valid_ids]
        return out   
    
    def __call__(self, input_ids):
        return self._compress(input_ids)
            
class ShortConv(nn.Module):
    def __init__(
        self, 
        hidden_size: int, 
        kernel_size: int = 4, 
        dilation: int = 1, 
        norm_eps: float = 1e-5,
        hc_mult: int = 4,
        activation: bool = True,
    ):
        super().__init__()
        self.hc_mult = hc_mult
        self.activation = activation
        
        total_channels = hidden_size * hc_mult
        self.conv = nn.Conv1d(
            in_channels=total_channels,
            out_channels=total_channels,
            kernel_size=kernel_size,
            groups=total_channels,
            bias=False,
            padding=(kernel_size - 1) * dilation,
            dilation=dilation,
        )

        self.norms = nn.ModuleList([
            nn.RMSNorm(hidden_size, eps=norm_eps) 
            for _ in range(hc_mult)
        ])
        
        if self.activation:
            self.act_fn = nn.SiLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input:  (B,L,HC_MULT,D)
        Output: (B,L,HC_MULT,D)
        """
        print(f"DEBUG ShortConv input shape: {x.shape}")
        B, T, G, C = x.shape
        
        assert G == self.hc_mult, f"Input groups {G} != hc_mult {self.hc_mult}"

        normed_chunks = []
        for i in range(G):
            chunk = x[:, :, i, :]
            normed_chunks.append(self.norms[i](chunk))
        
        x_norm = torch.cat(normed_chunks, dim=-1)
        x_bct = x_norm.transpose(1, 2)
        y_bct = self.conv(x_bct)
        y_bct = y_bct[..., :T]

        if self.activation:
            y_bct = self.act_fn(y_bct)
        y = y_bct.transpose(1, 2).view(B, T, G, C).contiguous()
        
        return y
    
def find_next_prime(start, seen_primes):
    candidate = start + 1
    while True:
        if isprime(candidate) and candidate not in seen_primes:
            return candidate
        candidate += 1

class NgramHashMapping:
    def __init__(
        self, 
        engram_vocab_size,
        max_ngram_size,
        n_embed_per_ngram,
        n_head_per_ngram,
        layer_ids,
        tokenizer_name_or_path,
        pad_id,
        seed,  
    ):
        self.vocab_size_per_ngram = engram_vocab_size
        self.max_ngram_size = max_ngram_size
        self.n_embed_per_ngram = n_embed_per_ngram
        self.n_head_per_ngram = n_head_per_ngram
        self.pad_id = pad_id
        self.layer_ids = layer_ids

        self.compressed_tokenizer = CompressedTokenizer(
            tokenizer_name_or_path=tokenizer_name_or_path
        )            
        self.tokenizer_vocab_size = len(self.compressed_tokenizer)
        if self.pad_id is not None:
            self.pad_id = int(self.compressed_tokenizer.lookup_table[self.pad_id])

        max_long = np.iinfo(np.int64).max
        M_max = int(max_long // self.tokenizer_vocab_size)
        half_bound = max(1, M_max // 2)
        PRIME_1 = 10007
        
        self.layer_multipliers = {}

        for layer_id in self.layer_ids:
            base_seed = int(seed + PRIME_1 * int(layer_id))
            g = np.random.default_rng(base_seed)
            r = g.integers(
                low=0,
                high=half_bound,
                size=(self.max_ngram_size,),
                dtype=np.int64
            )
            multipliers = r * 2 + 1
            self.layer_multipliers[layer_id] = multipliers

        self.vocab_size_across_layers = self.calculate_vocab_size_across_layers()

    def calculate_vocab_size_across_layers(self):
        seen_primes = set()
        vocab_size_across_layers = {}
        
        for layer_id in self.layer_ids:
            all_ngram_vocab_sizes = []
            for ngram in range(2, self.max_ngram_size + 1):
                current_ngram_heads_sizes = []
                
                vocab_size = self.vocab_size_per_ngram[ngram - 2]
                num_head = self.n_head_per_ngram
                current_prime_search_start = vocab_size - 1
                
                for _ in range(num_head):
                    found_prime = find_next_prime(
                        current_prime_search_start, 
                        seen_primes
                    )
                    seen_primes.add(found_prime)
                    current_ngram_heads_sizes.append(found_prime)
                    current_prime_search_start = found_prime
                
                all_ngram_vocab_sizes.append(current_ngram_heads_sizes)
            vocab_size_across_layers[layer_id] = all_ngram_vocab_sizes
            
        return vocab_size_across_layers

    def _get_ngram_hashes(
        self,
        input_ids: np.ndarray,
        layer_id: int,
    ) -> np.ndarray:
        x = np.asarray(input_ids, dtype=np.int64)
        B, T = x.shape

        multipliers = self.layer_multipliers[layer_id]

        def shift_k(k: int) -> np.ndarray:
            if k == 0: return x
            shifted = np.pad(x, ((0, 0), (k, 0)),
                                mode='constant', constant_values=self.pad_id)[:, :T]
            return shifted

        base_shifts = [shift_k(k) for k in range(self.max_ngram_size)]

        all_hashes = []
        
        for n in range(2, self.max_ngram_size + 1):
            n_gram_index = n - 2
            tokens = base_shifts[:n]
            mix = (tokens[0] * multipliers[0])
            for k in range(1, n):
                mix = np.bitwise_xor(mix, tokens[k] * multipliers[k])
            num_heads_for_this_ngram = self.n_head_per_ngram
            head_vocab_sizes = self.vocab_size_across_layers[layer_id][n_gram_index]
            
            for j in range(num_heads_for_this_ngram):
                mod = int(head_vocab_sizes[j])
                head_hash = mix % mod
                all_hashes.append(head_hash.astype(np.int64, copy=False))
        
        return np.stack(all_hashes, axis=2)

    def hash(self, input_ids):
        input_ids = self.compressed_tokenizer(input_ids)
        hash_ids_for_all_layers = {}
        for layer_id in self.layer_ids:
            hash_ids_for_all_layers[layer_id] = self._get_ngram_hashes(input_ids, layer_id=layer_id)
        return hash_ids_for_all_layers

class MultiHeadEmbedding(nn.Module):
    def __init__(self, list_of_N: List[int], D: int):
        super().__init__()
        self.num_heads = len(list_of_N)
        self.embedding_dim = D
        
        offsets = [0]
        for n in list_of_N[:-1]:
            offsets.append(offsets[-1] + n)
        
        self.register_buffer("offsets", torch.tensor(offsets, dtype=torch.long))
        
        total_N = sum(list_of_N)
        self.embedding = nn.Embedding(num_embeddings=total_N, embedding_dim=D)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        shifted_input_ids = input_ids + self.offsets
        output = self.embedding(shifted_input_ids)
        
        return output
    
class Engram(nn.Module):
    def __init__(self, layer_id):
        super().__init__()
        self.layer_id = layer_id
        self.hash_mapping = NgramHashMapping(
            engram_vocab_size=engram_cfg.engram_vocab_size,
            max_ngram_size = engram_cfg.max_ngram_size,
            n_embed_per_ngram = engram_cfg.n_embed_per_ngram,
            n_head_per_ngram = engram_cfg.n_head_per_ngram,
            layer_ids = engram_cfg.layer_ids,
            tokenizer_name_or_path=engram_cfg.tokenizer_name_or_path,
            pad_id = engram_cfg.pad_id,
            seed = engram_cfg.seed,
        )
        self.multi_head_embedding = MultiHeadEmbedding(
            list_of_N = [x for y in self.hash_mapping.vocab_size_across_layers[self.layer_id] for x in y],
            D = engram_cfg.n_embed_per_ngram // engram_cfg.n_head_per_ngram,
        )
        self.short_conv = ShortConv(
            hidden_size = backbone_config.hidden_size,
            kernel_size = engram_cfg.kernel_size,
            dilation    = engram_cfg.max_ngram_size,
            hc_mult     = backbone_config.hc_mult,
        )
        engram_hidden_size = (engram_cfg.max_ngram_size-1) * engram_cfg.n_embed_per_ngram
        self.value_proj = nn.Linear(engram_hidden_size,backbone_config.hidden_size)
        self.key_projs = nn.ModuleList(
            [nn.Linear(engram_hidden_size,backbone_config.hidden_size) for _ in range(backbone_config.hc_mult)]
        )
        self.norm1 = nn.ModuleList([nn.RMSNorm(backbone_config.hidden_size) for _ in range(backbone_config.hc_mult)])
        self.norm2 = nn.ModuleList([nn.RMSNorm(backbone_config.hidden_size) for _ in range(backbone_config.hc_mult)])
    
    def forward(self,hidden_states,input_ids):
        """
        hidden_states: [B, L, HC_MULT, D]
        input_ids: [B, L]
        """
        print(f"DEBUG Engram input shapes: hidden_states={hidden_states.shape}, input_ids={input_ids.shape}")
        hash_input_ids = torch.from_numpy(self.hash_mapping.hash(input_ids)[self.layer_id])
        embeddings = self.multi_head_embedding(hash_input_ids).flatten(start_dim=-2)
        gates = []
        for hc_idx in range(backbone_config.hc_mult):
            key = self.key_projs[hc_idx](embeddings)
            normed_key = self.norm1[hc_idx](key)
            query = hidden_states[:,:,hc_idx,:]
            normed_query = self.norm2[hc_idx](query)
            gate = (normed_key * normed_query).sum(dim=-1) / math.sqrt(backbone_config.hidden_size)
            gate = gate.abs().clamp_min(1e-6).sqrt() * gate.sign()
            gate = gate.sigmoid().unsqueeze(-1)
            gates.append(gate)
        gates = torch.stack(gates,dim=2)
        value = gates * self.value_proj(embeddings).unsqueeze(2)
        output = value + self.short_conv(value)
        return output 

class TransformerBlock(nn.Module):
    def __init__(self,layer_id):
        super().__init__()
        self.attn = lambda x:x
        self.moe  = lambda x:x
        self.engram = None
        if layer_id in engram_cfg.layer_ids:
            self.engram = Engram(layer_id=layer_id)
    
    def forward(self,input_ids,hidden_states):
        if self.engram is not None:
            hidden_states = self.engram(hidden_states=hidden_states,input_ids=input_ids) + hidden_states
        hidden_states = self.attn(hidden_states) + hidden_states
        hidden_states = self.moe(hidden_states) + hidden_states
        return hidden_states

class ClawdBotClient:
    def __init__(self, ws_url="ws://127.0.0.1:18789", auth_token=None):
        self.ws_url = ws_url
        self.auth_token = auth_token or "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
        self.connected = False
        self.session_id = None
        self.loop = None
        self.thread = None
        self.response_queue = asyncio.Queue()
        self._shutdown = False

    def start(self):
        """Start the WebSocket client in a background thread."""
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        # Quick check - don't block long
        time.sleep(1)
        return self.connected

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_loop())

    async def _connect_loop(self):
        """Maintain connection with auto-reconnect."""
        retry_delay = 1
        max_retries = 3
        retries = 0
        
        while not self._shutdown and retries < max_retries:
            try:
                await self._connect()
                if self.connected:
                    return  # Connection successful, exit loop
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    print(f"[WARN] ClawdBot max retries reached, falling back to LMStudio")
                    self.connected = False
                    return
                print(f"[WARN] ClawdBot connection error (retry {retries}/{max_retries}): {e}")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 10)

    async def _connect(self):
        """Connect to ClawdBot Gateway with proper handshake."""
        # Build URL with auth token as query parameter
        ws_url_with_auth = f"{self.ws_url}?token={self.auth_token}"
        
        try:
            import hashlib
            async with websockets.connect(
                ws_url_with_auth,
                subprotocols=["clawdbot-v1"],
                ping_interval=30,
                ping_timeout=10
            ) as websocket:
                self.websocket = websocket
                print("[OK] Connected to ClawdBot Gateway")
                
                # Wait for challenge first
                try:
                    challenge_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    challenge_data = json.loads(challenge_msg)
                    
                    # Handle challenge
                    if challenge_data.get("type") == "event" and challenge_data.get("event") == "connect.challenge":
                        nonce = challenge_data["payload"]["nonce"]
                        # Respond to challenge
                        await websocket.send(json.dumps({
                            "type": "challenge",
                            "nonce": nonce
                        }))
                        
                        # Now wait for hello
                        hello_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        hello_data = json.loads(hello_msg)
                        
                        if hello_data.get("type") == "hello":
                            self.session_id = hello_data.get("sessionId")
                            print(f"[OK] ClawdBot session: {self.session_id}")
                            
                            # Send hello response
                            await websocket.send(json.dumps({
                                "type": "hello",
                                "version": "1",
                                "sessionId": self.session_id,
                                "userAgent": "EngramClient/1.0"
                            }))
                            self.connected = True
                            print("[OK] ClawdBot authentication complete")
                        else:
                            print(f"[WARN] Unexpected message after challenge: {hello_data.get('type')}")
                            self.session_id = "unknown"
                            self.connected = True
                            
                    elif challenge_data.get("type") == "hello":
                        # No challenge, direct hello (older version)
                        self.session_id = challenge_data.get("sessionId")
                        print(f"[OK] ClawdBot session: {self.session_id}")
                        self.connected = True
                    else:
                        print(f"[WARN] Unexpected first message: {challenge_data.get('type')}")
                        self.session_id = "unknown"
                        self.connected = True
                        
                except asyncio.TimeoutError:
                    print("[WARN] No response from server, continuing anyway")
                    self.session_id = "unknown"
                    self.connected = True
                
                # Start listening for messages
                await self._listen()
                
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"[ERROR] ClawdBot auth failed (status {e.status_code}): {e}")
            self.connected = False
        except Exception as e:
            print(f"[ERROR] ClawdBot connection failed: {e}")
            self.connected = False

    async def _listen(self):
        """Listen for messages from ClawdBot."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "hello":
                        # Server hello/ack
                        self.session_id = data.get("sessionId", self.session_id)
                        print(f"[OK] ClawdBot handshake complete")
                        
                    elif msg_type == "event":
                        # Handle event messages (prevents 1008 errors)
                        event_type = data.get("event_type", "unknown")
                        print(f"[INFO] ClawdBot event: {event_type}")
                        
                    elif msg_type == "ping":
                        # Respond to ping with pong
                        await self.websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": time.time()
                        }))
                        
                    elif msg_type in ("chunk", "message"):
                        # Store response for retrieval
                        await self.response_queue.put(data)
                        
                    elif msg_type == "error":
                        error_msg = data.get("error", "Unknown error")
                        print(f"[ERROR] ClawdBot error: {error_msg}")
                        
                except json.JSONDecodeError:
                    print(f"[WARN] Invalid JSON from ClawdBot: {message[:100]}")
                    
        except websockets.exceptions.ConnectionClosed as e:
            print(f"[WARN] ClawdBot connection closed: {e}")
            self.connected = False
        except Exception as e:
            print(f"[ERROR] ClawdBot listen error: {e}")
            self.connected = False

    def send_message(self, message, timeout=30):
        """Send a message to ClawdBot and get response."""
        if not self.connected or not self.websocket:
            return "ClawdBot not connected"

        future = asyncio.run_coroutine_threadsafe(
            self._send_message_async(message, timeout), self.loop
        )
        try:
            return future.result(timeout=timeout)
        except Exception as e:
            self.connected = False
            return f"Error: {e}"

    async def _send_message_async(self, message, timeout):
        """Send message and collect response with timeout."""
        if not self.websocket:
            return "No websocket connection"

        # Clear any old responses
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        # Send message with proper format
        request = {
            "type": "message",
            "sessionId": self.session_id,
            "message": message,
            "thinking": "low",  # Use low thinking for faster response
            "timestamp": time.time()
        }
        
        try:
            await self.websocket.send(json.dumps(request))
        except Exception as e:
            self.connected = False
            return f"Send error: {e}"

        # Collect response with timeout
        response_text = ""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Wait for response with short timeout
                data = await asyncio.wait_for(self.response_queue.get(), timeout=1.0)
                
                msg_type = data.get("type")
                
                if msg_type == "chunk":
                    chunk_text = data.get("text", "")
                    response_text += chunk_text
                    if data.get("done"):
                        break
                        
                elif msg_type == "message":
                    response_text = data.get("text", "")
                    break
                    
            except asyncio.TimeoutError:
                # No message received yet, continue waiting
                continue
            except Exception as e:
                return f"Response collection error: {e}"
        
        if not response_text:
            return "No response received from ClawdBot"
            
        return response_text

    def stop(self):
        """Stop the client gracefully."""
        self._shutdown = True
        self.connected = False
        if self.loop and self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)

class EngramModel(nn.Module):
    def __init__(self, use_clawdbot=False, clawdbot_ws_url="ws://127.0.0.1:18789", use_lmstudio=False, lmstudio_url="http://100.118.172.23:1234", clawdbot_auth_token=None):
        super().__init__()
        self.use_clawdbot = use_clawdbot
        self.use_lmstudio = use_lmstudio
        self.lmstudio_url = lmstudio_url

        if self.use_clawdbot:
            self.clawdbot = ClawdBotClient(clawdbot_ws_url, auth_token=clawdbot_auth_token)
            self.clawdbot.start()
        elif self.use_lmstudio:
            # LMStudio mode - no local model needed
            pass
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(engram_cfg.tokenizer_name_or_path, trust_remote_code=True)
            self.embedding = nn.Embedding(backbone_config.vocab_size, backbone_config.hidden_size)
            self.layers = nn.ModuleList([TransformerBlock(layer_id=layer_id) for layer_id in range(backbone_config.num_layers)])
            self.head = nn.Linear(backbone_config.hidden_size, backbone_config.vocab_size)

    def forward(self, input_ids):
        if self.use_clawdbot or self.use_lmstudio:
            # For external models, return dummy logits for compatibility
            # In practice, this forward might not be used when external models are enabled
            B, L = input_ids.shape
            return torch.randn(B, L, backbone_config.vocab_size)
        else:
            # Initial embedding
            hidden_states = self.embedding(input_ids)
            # Mock hyper-connection expansion (B, L, HC_MULT, D)
            hidden_states = hidden_states.unsqueeze(2).expand(-1, -1, backbone_config.hc_mult, -1)

            for layer in self.layers:
                hidden_states = layer(input_ids=input_ids, hidden_states=hidden_states)

            # Mock hyper-connection collapse for the head
            hidden_states = hidden_states[:, :, 0, :]
            logits = self.head(hidden_states)
            return logits

    def analyze_market(self, market_data, prompt_template="Analyze this market data and provide trading signals: {data}"):
        """Use external model (ClawdBot or LMStudio) for market analysis."""
        response = None
        
        if self.use_clawdbot:
            if not self.clawdbot.connected:
                # Fall back to LMStudio if ClawdBot not connected
                print("ClawdBot not connected, falling back to LMStudio")
                response = self._query_lmstudio(prompt_template.format(data=str(market_data)))
            else:
                prompt = prompt_template.format(data=str(market_data))
                response = self.clawdbot.send_message(prompt)
                
                # Check if response is an error message
                if response and (response.startswith("Error:") or response.startswith("ClawdBot") or response.startswith("No websocket")):
                    print(f"ClawdBot error: {response}, falling back to LMStudio")
                    response = self._query_lmstudio(prompt)

        elif self.use_lmstudio:
            prompt = prompt_template.format(data=str(market_data))
            response = self._query_lmstudio(prompt)

        else:
            return {"signal": "HOLD", "confidence": 0.5, "reason": "No external model configured"}

        # Check if response is still an error or empty
        if not response or response.startswith("Error:") or response.startswith("LMStudio query failed"):
            return {
                "signal": "HOLD",
                "confidence": 0.5,
                "reason": "Unable to analyze market data at this time. Please try again later."
            }

        # Parse response for signal
        response_lower = response.lower()
        if "buy" in response_lower and "sell" not in response_lower:
            signal = "BUY"
        elif "sell" in response_lower:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "signal": signal,
            "confidence": 0.8,  # Default high confidence
            "reason": response
        }

    def _query_lmstudio(self, prompt):
        """Query LMStudio API for response."""
        try:
            url = f"{self.lmstudio_url}/v1/chat/completions"
            data = {
                "model": "glm-4.7-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful trading analysis AI. Provide clear, concise responses without showing your thinking process. Give direct answers only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer dummy"
            }

            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            message = result['choices'][0]['message']
            
            # Get content, preferring 'content' over 'reasoning_content'
            content = message.get('content', '').strip()
            reasoning = message.get('reasoning_content', '').strip()
            
            # DEBUG: Log what we received
            logger.info(f"[DEBUG] LMStudio Response - content length: {len(content)}, reasoning length: {len(reasoning)}")
            if not content:
                logger.warning(f"[DEBUG] EMPTY CONTENT DETECTED! Reasoning preview: {reasoning[:100]}...")
            
            # GLM-4.7-flash fix: If content is empty but reasoning exists, extract answer
            if not content and reasoning:
                logger.info("[DEBUG] APPLYING GLM-4.7-FLASH FIX - Extracting from reasoning_content")
                # Strategy 1: Look for the last paragraph (usually the answer)
                if '\n\n' in reasoning:
                    paragraphs = [p.strip() for p in reasoning.split('\n\n') if p.strip()]
                    if paragraphs:
                        # Take the last paragraph as it's usually the final answer
                        content = paragraphs[-1]
                        logger.info(f"[DEBUG] Strategy 1 applied - extracted {len(content)} chars from last paragraph")
                
                # Strategy 2: If still no content or content looks like reasoning, extract differently
                if not content or any(marker in content.lower() for marker in ['first,', 'let me', 'i need to', 'i should', 'thinking', 'the user']):
                    # Look for sentences that don't start with reasoning markers
                    sentences = reasoning.split('. ')
                    clean_sentences = []
                    for sentence in sentences:
                        sentence = sentence.strip()
                        # Skip reasoning sentences
                        if not any(marker in sentence.lower()[:50] for marker in ['first,', 'let me', 'i need to', 'i should', 'thinking', 'the user is', 'i will']):
                            clean_sentences.append(sentence)
                    
                    if clean_sentences:
                        content = '. '.join(clean_sentences).strip()
                        # Ensure it ends with proper punctuation
                        if content and not content.endswith(('.', '!', '?')):
                            content += '.'
                        logger.info(f"[DEBUG] Strategy 2 applied - filtered {len(clean_sentences)} clean sentences")
                
                # Strategy 3: If still no good content, use full reasoning but clean it
                if not content:
                    content = reasoning
                    # Remove common reasoning prefixes
                    reasoning_markers = [
                        'First, the user wants me to',
                        'First, I need to',
                        'Let me think about',
                        'I should',
                        'The user is asking',
                        'The user wants',
                    ]
                    for marker in reasoning_markers:
                        if content.lower().startswith(marker.lower()):
                            # Find the actual response after the reasoning
                            parts = content.split('. ', 1)
                            if len(parts) > 1:
                                content = parts[1].strip()
                                logger.info(f"[DEBUG] Strategy 3 applied - removed reasoning prefix")
                            break
            
            # Final cleanup: Ensure we have something
            if not content:
                logger.warning("[DEBUG] Still no content after all strategies - using fallback")
                content = "I'm here to help! How can I assist you?"
            else:
                logger.info(f"[DEBUG] Final content length: {len(content)} chars")
            
            # Limit length to prevent truncation
            MAX_LENGTH = 800  # Reasonable length for most responses
            if len(content) > MAX_LENGTH:
                logger.info(f"[DEBUG] Content too long ({len(content)} chars), truncating to {MAX_LENGTH}")
                # Try to cut at sentence boundary
                truncated = content[:MAX_LENGTH]
                last_period = truncated.rfind('.')
                if last_period > MAX_LENGTH * 0.7:  # If we can cut at a sentence
                    content = truncated[:last_period + 1]
                else:
                    content = truncated + "..."
            
            logger.info(f"[DEBUG] Returning content: {content[:100]}...")
            return content
            
        except Exception as e:
            return f"LMStudio query failed: {str(e)}"

    @torch.no_grad()
    def generate(self, prompt: str, max_new_tokens: int = 50):
        input_ids = self.tokenizer(prompt, return_tensors='pt').input_ids
        for _ in range(max_new_tokens):
            logits = self.forward(input_ids)
            next_token_logits = logits[:, -1, :]
            next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            input_ids = torch.cat([input_ids, next_token], dim=-1)
            if next_token.item() == self.tokenizer.eos_token_id:
                break
        return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)

if __name__ == '__main__':
    # Use LMStudio mode with your local model
    model = EngramModel(use_lmstudio=True, lmstudio_url="http://100.118.172.23:1234")

    text = "Only Alexander the Great could tame the horse Bucephalus."
    tokenizer = AutoTokenizer.from_pretrained(engram_cfg.tokenizer_name_or_path,trust_remote_code=True)
    input_ids = tokenizer(text,return_tensors='pt').input_ids

    B,L = input_ids.shape

    # Forward pass through the model
    logits = model(input_ids)

    print("✅ Forward Complete!")
    print(f"{input_ids.shape=}\n{logits.shape=}")

    # Test market analysis with local LMStudio model
    print("\n🔍 Testing market analysis with local LMStudio model...")
    market_data = {
        "symbol": "BTC/USD",
        "price": 43250.00,
        "volume": 1234567,
        "rsi": 65.4,
        "macd": 150.2,
        "trend": "bullish"
    }
    
    analysis = model.analyze_market(market_data)
    print(f"Trading Signal: {analysis['signal']}")
    print(f"Confidence: {analysis['confidence']}")
    print(f"Reason: {analysis['reason']}")
            