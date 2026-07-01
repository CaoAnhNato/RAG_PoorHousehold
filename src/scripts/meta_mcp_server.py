# -*- coding: utf-8 -*-
"""
Meta MCP Server Wrapper
Aggregates GitNexus, CodeGraphContext, and Lean-Ctx MCP servers.
Implements:
1. Meta-tool: meta_deep_context
2. Smart hints injection: _agent_hint in responses
"""
import asyncio
import json
import os
import sys
import re
import traceback

LOG_FILE = os.path.expandvars(r"C:\Users\Admin\.gemini\antigravity\meta_mcp_server.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except:
        pass

class ChildServer:
    def __init__(self, name, command, args, env=None, cwd=None):
        self.name = name
        self.command = command
        self.args = args
        self.env = env
        self.cwd = cwd
        self.process = None
        self.reader = None
        self.writer = None

    async def start(self):
        log(f"Starting child server {self.name}: {self.command} {' '.join(self.args)}")
        # Merge environment
        merged_env = os.environ.copy()
        if self.env:
            for k, v in self.env.items():
                merged_env[k] = str(v)
        
        import shutil
        resolved_cmd = shutil.which(self.command) or self.command
        log(f"Resolved command for {self.name}: {resolved_cmd}")

        self.process = await asyncio.create_subprocess_exec(
            resolved_cmd,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=merged_env,
            cwd=self.cwd,
            limit=1024 * 1024 * 32  # 32MB limit for large JSON-RPC messages
        )
        self.reader = self.process.stdout
        self.writer = self.process.stdin
        log(f"Child server {self.name} started (PID: {self.process.pid})")

    async def send(self, msg_dict):
        if not self.writer:
            return
        line = json.dumps(msg_dict) + "\n"
        self.writer.write(line.encode("utf-8"))
        await self.writer.drain()

    async def stop(self):
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                log(f"Error closing writer for {self.name}: {e}")
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(self.process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                try:
                    self.process.kill()
                    await self.process.wait()
                except ProcessLookupError:
                    pass
        log(f"Child {self.name} stopped.")

class MetaMCPServer:
    def __init__(self):
        self.children = {}
        self.tool_to_child = {}
        self.pending_requests = {}
        self.next_internal_id = 1
        self.client_reader = None
        self.client_writer = None
        self.initialized = False
        self.initialize_client_req = None
        self.stdin_queue = None
        self.chart_http_server = None

    def load_config(self):
        config_path = r"C:\Users\Admin\.gemini\antigravity\mcp_config.json"
        if not os.path.exists(config_path):
            log(f"Config path {config_path} not found.")
            return False

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            servers_config = config.get("mcpServers", {})
            
            # Load gitnexus
            if "gitnexus" in servers_config:
                c = servers_config["gitnexus"]
                self.children["gitnexus"] = ChildServer(
                    "gitnexus",
                    c.get("command", "gitnexus"),
                    c.get("args", ["mcp"]),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
            
            # Load codegraphcontext
            if "codegraphcontext" in servers_config:
                c = servers_config["codegraphcontext"]
                self.children["codegraphcontext"] = ChildServer(
                    "codegraphcontext",
                    c.get("command"),
                    c.get("args", ["mcp", "start"]),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )

            # Load lean-ctx
            if "lean-ctx" in servers_config:
                c = servers_config["lean-ctx"]
                self.children["lean-ctx"] = ChildServer(
                    "lean-ctx",
                    c.get("command"),
                    c.get("args", []),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
                
            # Load exa
            if "exa" in servers_config:
                c = servers_config["exa"]
                self.children["exa"] = ChildServer(
                    "exa",
                    c.get("command"),
                    c.get("args", []),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
                
            # Load arxiv
            if "arxiv" in servers_config:
                c = servers_config["arxiv"]
                self.children["arxiv"] = ChildServer(
                    "arxiv",
                    c.get("command"),
                    c.get("args", []),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
                
            # Load octocode
            if "octocode" in servers_config:
                c = servers_config["octocode"]
                self.children["octocode"] = ChildServer(
                    "octocode",
                    c.get("command"),
                    c.get("args", []),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
                
            # Load fetch
            if "fetch" in servers_config:
                c = servers_config["fetch"]
                self.children["fetch"] = ChildServer(
                    "fetch",
                    c.get("command"),
                    c.get("args", []),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
                
            # Load firecrawl
            if "firecrawl" in servers_config:
                c = servers_config["firecrawl"]
                self.children["firecrawl"] = ChildServer(
                    "firecrawl",
                    c.get("command"),
                    c.get("args", []),
                    env=c.get("env"),
                    cwd=c.get("cwd")
                )
                
            return True
        except Exception as e:
            log(f"Error loading config: {e}")
            return False

    async def start(self):
        self.load_config()
        
        # Start child servers
        for name, child in list(self.children.items()):
            try:
                await child.start()
                # Start stdout and stderr reading tasks for this child
                asyncio.create_task(self.read_child_stdout(child))
                asyncio.create_task(self.read_child_stderr(child))
            except Exception as e:
                log(f"Failed to start child {name}: {e}")
                del self.children[name]

        log("Meta MCP Server started and ready for client messages (Windows-safe stdio)")
        
        # Set up async Queue for stdin lines
        self.stdin_queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        
        # Start background thread to read from raw stdin (fd 0)
        import threading
        def stdin_reader_thread():
            buffer = b""
            while True:
                try:
                    chunk = os.read(0, 8192)
                    if not chunk:
                        # EOF
                        loop.call_soon_threadsafe(self.stdin_queue.put_nowait, None)
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        loop.call_soon_threadsafe(self.stdin_queue.put_nowait, line.decode("utf-8", errors="replace"))
                except Exception as e:
                    log(f"Error in stdin_reader_thread: {e}")
                    loop.call_soon_threadsafe(self.stdin_queue.put_nowait, None)
                    break
        
        threading.Thread(target=stdin_reader_thread, daemon=True).start()
        
        # Process lines from the queue
        while True:
            line = await self.stdin_queue.get()
            if line is None:
                log("Client connection closed (EOF).")
                break
            try:
                msg = json.loads(line.strip())
                await self.handle_client_msg(msg)
            except Exception as e:
                log(f"Error processing client msg: {e}\n{traceback.format_exc()}")

    async def send_to_client(self, msg_dict):
        line = json.dumps(msg_dict) + "\n"
        loop = asyncio.get_running_loop()
        
        def write_sync(l):
            try:
                os.write(1, l.encode("utf-8", errors="replace"))
            except Exception as e:
                log(f"Error in write_sync: {e}")
                
        await loop.run_in_executor(None, write_sync, line)

    async def read_child_stdout(self, child):
        while True:
            try:
                line = await child.reader.readline()
                if not line:
                    log(f"Child {child.name} stdout closed (Process exited).")
                    await self.handle_child_death(child)
                    break
                
                msg = json.loads(line.decode("utf-8", errors="replace"))
                await self.handle_child_msg(child, msg)
            except Exception as e:
                log(f"Error reading {child.name} stdout: {e}")
                await asyncio.sleep(0.1)

    async def read_child_stderr(self, child):
        while True:
            try:
                line = await child.process.stderr.readline()
                if not line:
                    break
                log(f"[{child.name} STDERR] {line.decode('utf-8', errors='replace').strip()}")
            except Exception as e:
                log(f"Error reading {child.name} stderr: {e}")
                break

    async def stop(self):
        log("Shutting down MetaMCPServer...")
        for name, child in list(self.children.items()):
            await child.stop()
        self.children.clear()
        log("All child servers stopped.")

    async def handle_child_death(self, child):
        if child.name in self.children:
            del self.children[child.name]
            log(f"Removed dead child {child.name}. Active children remaining: {list(self.children.keys())}")
            await child.stop()
        
        # Resolve pending tools_list requests if they were waiting for this child
        keys_to_resolve = []
        for key, req in list(self.pending_requests.items()):
            if key.startswith("tools_list:"):
                if child.name not in req["responses"]:
                    req["responses"][child.name] = []
                    if len(req["responses"]) >= req["expected"]:
                        keys_to_resolve.append(key)
        
        for key in keys_to_resolve:
            req = self.pending_requests[key]
            client_id = req["client_id"]
            
            all_tools = []
            for c_name, tools in req["responses"].items():
                for tool in tools:
                    all_tools.append(tool)
                    self.tool_to_child[tool["name"]] = c_name
            
            # Inject meta tools
            self.add_meta_tools_to_list(all_tools)
            
            list_res = {
                "jsonrpc": "2.0",
                "id": client_id,
                "result": {
                    "tools": all_tools
                }
            }
            await self.send_to_client(list_res)
            self.pending_requests.pop(key, None)

    async def tools_list_timeout(self, req_key, timeout_val):
        await asyncio.sleep(timeout_val)
        if req_key in self.pending_requests:
            req = self.pending_requests[req_key]
            client_id = req["client_id"]
            log(f"Timeout reached for tools/list request {client_id}. Resolving with partial results.")
            
            # For any child that didn't respond, set its response to empty list
            for child_name in list(self.children.keys()):
                if child_name not in req["responses"]:
                    req["responses"][child_name] = []
            
            all_tools = []
            for c_name, tools in req["responses"].items():
                for tool in tools:
                    all_tools.append(tool)
                    self.tool_to_child[tool["name"]] = c_name
            
            self.add_meta_tools_to_list(all_tools)
            
            list_res = {
                "jsonrpc": "2.0",
                "id": client_id,
                "result": {
                    "tools": all_tools
                }
            }
            await self.send_to_client(list_res)
            self.pending_requests.pop(req_key, None)

    async def client_call_timeout(self, req_key, timeout_val):
        await asyncio.sleep(timeout_val)
        if req_key in self.pending_requests:
            req = self.pending_requests[req_key]
            client_id = req["client_id"]
            child_name = req["child_name"]
            log(f"Timeout reached for client tool call {client_id} to child {child_name}.")
            
            err_res = {
                "jsonrpc": "2.0",
                "id": client_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool call timed out after {timeout_val} seconds"
                }
            }
            await self.send_to_client(err_res)
            self.pending_requests.pop(req_key, None)
            
            # Send cancellation to the child
            child = self.children.get(child_name)
            if child:
                cancel_msg = {
                    "jsonrpc": "2.0",
                    "method": "$/cancelRequest",
                    "params": {
                        "id": f"{child.name}:call:{client_id}"
                    }
                }
                await child.send(cancel_msg)
                log(f"Sent cancellation request to {child_name} for call {client_id}")

    async def handle_client_msg(self, msg):
        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            self.initialize_client_req = msg
            # Forward initialize to all children
            for child in self.children.values():
                child_init = {
                    "jsonrpc": "2.0",
                    "id": f"{child.name}:init",
                    "method": "initialize",
                    "params": msg.get("params", {})
                }
                await child.send(child_init)
            
            # Respond to client with our capabilities
            init_res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "meta-agent-helper",
                        "version": "1.0.0"
                    }
                }
            }
            await self.send_to_client(init_res)
            self.initialized = True
            log("Responded to client initialize request")
            return

        if not self.initialized:
            log("Ignoring client message before initialize")
            return

        if method == "initialized" or method == "notifications/initialized":
            # Forward initialized notification to all children
            for child in self.children.values():
                await child.send({
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                })
            return

        if method == "tools/list":
            if not self.children:
                all_tools = []
                self.add_meta_tools_to_list(all_tools)
                list_res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": all_tools
                    }
                }
                await self.send_to_client(list_res)
                return
            
            req_key = f"tools_list:{msg_id}"
            # Query all children for their tools
            self.pending_requests[req_key] = {
                "client_id": msg_id,
                "responses": {},
                "expected": len(self.children)
            }
            for child in self.children.values():
                await child.send({
                    "jsonrpc": "2.0",
                    "id": f"{child.name}:tools_list:{msg_id}",
                    "method": "tools/list"
                })
            
            # Schedule a timeout of 5.0 seconds
            asyncio.create_task(self.tools_list_timeout(req_key, 5.0))
            return

        if method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name in ["meta_deep_context", "meta_explore_structure", "meta_safe_edit_preview", "meta_trace_flow", "meta_research_idea", "visual_start_chart_server", "visual_playwright_screenshot", "visual_extract_dom_boxes", "visual_check_wcag_contrast"]:
                async def run_with_timeout():
                    try:
                        if tool_name == "meta_deep_context":
                            await asyncio.wait_for(self.handle_meta_deep_context(msg_id, arguments), timeout=180.0)
                        elif tool_name == "meta_explore_structure":
                            await asyncio.wait_for(self.handle_meta_explore_structure(msg_id, arguments), timeout=180.0)
                        elif tool_name == "meta_safe_edit_preview":
                            await asyncio.wait_for(self.handle_meta_safe_edit_preview(msg_id, arguments), timeout=180.0)
                        elif tool_name == "meta_trace_flow":
                            await asyncio.wait_for(self.handle_meta_trace_flow(msg_id, arguments), timeout=180.0)
                        elif tool_name == "meta_research_idea":
                            await asyncio.wait_for(self.handle_meta_research_idea(msg_id, arguments), timeout=180.0)
                        elif tool_name == "visual_start_chart_server":
                            await asyncio.wait_for(self.handle_visual_start_chart_server(msg_id, arguments), timeout=60.0)
                        elif tool_name == "visual_playwright_screenshot":
                            await asyncio.wait_for(self.handle_visual_playwright_screenshot(msg_id, arguments), timeout=120.0)
                        elif tool_name == "visual_extract_dom_boxes":
                            await asyncio.wait_for(self.handle_visual_extract_dom_boxes(msg_id, arguments), timeout=120.0)
                        elif tool_name == "visual_check_wcag_contrast":
                            await asyncio.wait_for(self.handle_visual_check_wcag_contrast(msg_id, arguments), timeout=60.0)
                    except asyncio.TimeoutError:
                        log(f"Meta-tool {tool_name} timed out for {msg_id}")
                        await self.send_to_client({
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32603,
                                "message": f"Meta-tool {tool_name} timed out after 60.0 seconds"
                            }
                        })
                    except Exception as e:
                        log(f"Error in {tool_name}: {e}\n{traceback.format_exc()}")
                        await self.send_to_client({
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32603,
                                "message": f"Error in {tool_name}: {e}"
                            }
                        })
                        
                asyncio.create_task(run_with_timeout())
                return

            # Determine which child owns the tool
            child_name = self.tool_to_child.get(tool_name)
            if child_name and child_name in self.children:
                child = self.children[child_name]
                # Forward to child
                child_req = {
                    "jsonrpc": "2.0",
                    "id": f"{child.name}:call:{msg_id}",
                    "method": "tools/call",
                    "params": params
                }
                
                req_key = f"client_call:{child.name}:{msg_id}"
                self.pending_requests[req_key] = {
                    "client_id": msg_id,
                    "child_name": child_name
                }
                
                await child.send(child_req)
                
                # Schedule timeout of 30.0 seconds for forwarded tool call
                asyncio.create_task(self.client_call_timeout(req_key, 30.0))
            else:
                # Tool not found
                err_res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool {tool_name} not found"
                    }
                }
                await self.send_to_client(err_res)
            return

        # Generic forwarding for other requests/notifications
        if msg_id is not None:
            # We don't know where to route it, so route to first child or drop
            first_child = list(self.children.values())[0] if self.children else None
            if first_child:
                await first_child.send({
                    "jsonrpc": "2.0",
                    "id": f"{first_child.name}:generic:{msg_id}",
                    "method": method,
                    "params": msg.get("params", {})
                })
        else:
            # Broadcast notifications
            for child in self.children.values():
                await child.send(msg)

    async def handle_child_msg(self, child, msg):
        msg_id = msg.get("id")
        if msg_id is None:
            # Notification from child, ignore or forward to client if appropriate
            return

        # Parse wrapped ID
        id_str = str(msg_id)
        
        if id_str.endswith(":init"):
            # Child initialized, just log
            log(f"Child {child.name} initialize response received")
            return

        if ":tools_list:" in id_str:
            # Tools list response
            parts = id_str.split(":tools_list:")
            child_name = parts[0]
            msg_id_str = parts[1]
            
            matched_key = None
            client_id = None
            for key, req in self.pending_requests.items():
                if key.startswith("tools_list:") and str(req.get("client_id", "")) == msg_id_str:
                    matched_key = key
                    client_id = req["client_id"]
                    break
                    
            if matched_key:
                req_state = self.pending_requests[matched_key]
                req_state["responses"][child.name] = msg.get("result", {}).get("tools", [])
                
                if len(req_state["responses"]) >= req_state["expected"]:
                    # All children replied, merge results
                    all_tools = []
                    
                    # Tool Whitelist to expose ONLY essential tools to the IDE (Agent)
                    # We hide raw tools from CGC/GitNexus because they are wrapped by our 5 meta_ workflows
                    # This reduces tool bloat (from 57 to ~16) and FORCES the Agent to use safe Meta-Workflows.
                    allowed_tools = {
                        # Lean-Ctx essentials
                        "ctx_read", "ctx_edit", "ctx_search", "ctx_shell", "ctx_tree", "ctx_semantic_search", "ctx_knowledge", "ctx_session",
                        # GitNexus essentials
                        "query", "detect_changes", "list_repos"
                    }
                    
                    for c_name, tools in req_state["responses"].items():
                        for tool in tools:
                            # Always register in internal router so Meta-Tools can call them
                            self.tool_to_child[tool["name"]] = c_name
                            
                            # Only expose whitelisted tools to the Agent/IDE
                            if tool["name"] in allowed_tools:
                                all_tools.append(tool)
                    
                    self.add_meta_tools_to_list(all_tools)
                    
                    # Respond to client
                    list_res = {
                        "jsonrpc": "2.0",
                        "id": client_id,
                        "result": {
                            "tools": all_tools
                        }
                    }
                    await self.send_to_client(list_res)
                    self.pending_requests.pop(matched_key, None)
            return

        if ":internal_call:" in id_str:
            parts = id_str.split(":internal_call:")
            internal_id = int(parts[1])
            req_key = f"internal_call:{internal_id}"
            
            if req_key in self.pending_requests:
                fut = self.pending_requests[req_key]
                if not fut.done():
                    if "error" in msg:
                        fut.set_exception(Exception(str(msg["error"])))
                    else:
                        fut.set_result(msg.get("result", {}))
            return

        if ":call:" in id_str:
            # Tool call response
            parts = id_str.split(":call:")
            child_name = parts[0]
            msg_id_str = parts[1]
            
            matched_key = None
            client_id = None
            for key, req in self.pending_requests.items():
                if key.startswith(f"client_call:{child_name}:") and str(req.get("client_id", "")) == msg_id_str:
                    matched_key = key
                    client_id = req["client_id"]
                    break
            
            if matched_key:
                self.pending_requests.pop(matched_key, None)
                
                # Intercept response to inject smart hints
                if "result" in msg:
                    result = msg["result"]
                    # Add smart hints to the result
                    result = self.inject_smart_hints(child.name, id_str, result)
                    res_msg = {
                        "jsonrpc": "2.0",
                        "id": client_id,
                        "result": result
                    }
                else:
                    res_msg = {
                        "jsonrpc": "2.0",
                        "id": client_id,
                        "error": msg.get("error")
                    }
                
                await self.send_to_client(res_msg)
            return

    async def handle_meta_deep_context(self, client_id, arguments):
        symbol_name = arguments.get("symbol_name")
        intent = arguments.get("intent")
        
        log(f"Handling meta_deep_context for {symbol_name} with intent {intent}")
        
        # Prepare requests
        tasks = []
        
        # 1. Get symbol context (GitNexus or CGC)
        if "gitnexus" in self.children:
            tasks.append(self.call_child_tool_internal("gitnexus", "context", {"name": symbol_name}))
        elif "codegraphcontext" in self.children:
            tasks.append(self.call_child_tool_internal("codegraphcontext", "find_code", {"query": symbol_name}))
            
        # 2. Get impact analysis for refactor/rename
        if intent in ["refactor", "rename"]:
            if "gitnexus" in self.children:
                tasks.append(self.call_child_tool_internal("gitnexus", "impact", {
                    "target": symbol_name,
                    "direction": "upstream",
                    "summaryOnly": True
                }))
            if "codegraphcontext" in self.children:
                tasks.append(self.call_child_tool_internal("codegraphcontext", "analyze_code_relationships", {
                    "target": symbol_name,
                    "query_type": "find_all_callers"
                }))
                
        # 3. Get callers / complexity for debug
        if intent == "debug":
            if "codegraphcontext" in self.children:
                tasks.append(self.call_child_tool_internal("codegraphcontext", "analyze_code_relationships", {
                    "target": symbol_name,
                    "query_type": "find_callers"
                }))
                tasks.append(self.call_child_tool_internal("codegraphcontext", "calculate_cyclomatic_complexity", {
                    "function_name": symbol_name
                }))

        # Wait for all tools
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results into a clean markdown
        markdown_sections = [f"# Meta-Context Analysis for `{symbol_name}` (Intent: {intent})"]
        
        for r in results:
            if isinstance(r, Exception):
                continue
            if not r or "error" in r:
                continue
            
            tool_name = r.get("tool_name")
            content = r.get("content", "")
            
            markdown_sections.append(f"## Tool Result: `{tool_name}`")
            markdown_sections.append(content)
            
        # Compile response
        merged_text = "\n\n".join(markdown_sections)
        
        # Create smart hints specifically for meta_deep_context
        hints = self.generate_hints_for_meta(symbol_name, intent, merged_text)
        
        response_content = [
            {
                "type": "text",
                "text": merged_text
            },
            {
                "type": "text",
                "text": f"\n\n---\n### 💡 Smart Hints\n```json\n{json.dumps(hints, indent=2, ensure_ascii=False)}\n```"
            }
        ]
        
        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": response_content
            }
        })

    async def handle_meta_research_idea(self, client_id, arguments):
        query = arguments.get("query", "")
        source = arguments.get("source", "both")
        
        log(f"Handling meta_research_idea for '{query}' in {source}")
        
        tasks = []
        source_names = []
        
        def extract_text_from_result(res):
            content_obj = res.get("content", res) if isinstance(res, dict) else res
            content_str = ""
            if isinstance(content_obj, str):
                content_str = content_obj
            elif isinstance(content_obj, list):
                for item in content_obj:
                    if isinstance(item, dict) and "text" in item:
                        content_str += item["text"] + "\n"
                    else:
                        content_str += str(item) + "\n"
            else:
                content_str = str(content_obj)
            return content_str

        if source in ["web", "both"] and "firecrawl" in self.children:
            async def search_web_firecrawl(q):
                try:
                    res = await asyncio.wait_for(self.call_child_tool_internal("firecrawl", "firecrawl_search", {
                        "query": q,
                        "limit": 8
                    }), timeout=90.0)
                    
                    if isinstance(res, dict) and "error" in res and res["error"]:
                        return {"tool_name": "firecrawl", "error": f"Search returned error: {res['error']}"}

                    content_obj = res.get("content", res) if isinstance(res, dict) else res
                    extracted_text = ""
                    
                    def process_json_item(data):
                        nonlocal extracted_text
                        web_data = data.get("data", {}).get("web", [])
                        if not web_data and "web" in data:
                            web_data = data["web"]
                        if web_data:
                            for doc in web_data:
                                url = doc.get("url", "Unknown URL")
                                title = doc.get("title", "Unknown Title")
                                desc = doc.get("description", "No description available.")
                                
                                extracted_text += f"### 🌐 {title}\n**URL:** {url}\n**Summary:** {desc}\n\n"
                        else:
                            extracted_text += f"No web results found. Keys: {list(data.keys())}\n\n"

                    if isinstance(content_obj, list):
                        for item in content_obj:
                            if isinstance(item, dict) and "text" in item:
                                try:
                                    import json
                                    data = json.loads(item["text"])
                                    process_json_item(data)
                                except Exception as e:
                                    extracted_text += f"Failed to parse JSON: {e}\n\n{str(item['text'])[:500]}\n\n"
                            else:
                                extracted_text += str(item)[:500] + "\n"
                    elif isinstance(content_obj, str):
                        try:
                            import json
                            data = json.loads(content_obj)
                            process_json_item(data)
                        except:
                            extracted_text += content_obj[:1500]
                    else:
                        extracted_text += str(content_obj)[:1500]
                        
                    return {"tool_name": "firecrawl", "content": extracted_text}
                except Exception as e:
                    return {"tool_name": "firecrawl", "error": f"Web search failed or timed out: {e}"}
                    
            tasks.append(search_web_firecrawl(query))
            source_names.append("🌐 Web Search (Articles & Documentation)")
            
        if source in ["github", "both", "web"] and "octocode" in self.children:
            async def search_github_deep(q):
                if "octocode" in self.children:
                    try:
                        import re
                        search_keywords = [kw for kw in re.split(r'\W+', q) if len(kw) > 3][:3]
                        if not search_keywords:
                            search_keywords = [q.replace(" ", "-")[:50]]
                        search_res = await asyncio.wait_for(self.call_child_tool_internal("octocode", "githubSearchRepositories", {
                            "queries": [{"keywordsToSearch": search_keywords, "sort": "best-match"}]
                        }), timeout=60.0)

                        if isinstance(search_res, dict) and "error" in search_res and search_res["error"]:
                            return {"tool_name": "octocode", "error": f"Search returned error: {search_res['error']}"}

                        content_str = extract_text_from_result(search_res)
                        repos = []
                        # Robust extraction for GitHub repos from JSON strings or raw text
                        import json
                        try:
                            # Try parsing if it's wrapped in text JSON
                            content_obj = search_res.get("content", search_res) if isinstance(search_res, dict) else search_res
                            if isinstance(content_obj, list):
                                for item in content_obj:
                                    if isinstance(item, dict) and "text" in item:
                                        data = json.loads(item["text"])
                                        items = data.get("items", data) if isinstance(data, dict) else data
                                        if isinstance(items, list):
                                            for r in items:
                                                owner = r.get("owner", {}).get("login") if isinstance(r.get("owner"), dict) else r.get("owner")
                                                name = r.get("name")
                                                if owner and name:
                                                    repos.append((owner, name))
                        except:
                            pass

                        if not repos:
                            # Regex fallback
                            matches = re.findall(r'full_name["\'\s:]+([A-Za-z0-9_\-\.]+)/([A-Za-z0-9_\-\.]+)', content_str, re.IGNORECASE)
                            repos.extend(matches)
                            if not repos:
                                matches = re.findall(r'owner["\'\s:]+([A-Za-z0-9_\-\.]+).*?name["\'\s:]+([A-Za-z0-9_\-\.]+)', content_str, re.IGNORECASE | re.DOTALL)
                                repos.extend(matches)
                            if not repos:
                                repos = re.findall(r'github\.com/([A-Za-z0-9_\-\.]+)/([A-Za-z0-9_\-\.]+)', content_str)

                        # Deduplicate while preserving order
                        seen = set()
                        repos = [r for r in repos if not (r in seen or seen.add(r))]

                        if not repos:
                            return {"tool_name": "octocode", "content": f"No repositories found for keywords {search_keywords}. Output was:\n{content_str[:500]}"}

                        # 2. Fetch READMEs and Code Structure
                        readme_tasks = []
                        for owner, repo in repos[:3]:
                            readme_tasks.append(asyncio.wait_for(self.call_child_tool_internal("octocode", "githubGetFileContent", {
                                "queries": [{"owner": owner, "repo": repo, "path": "README.md", "fullContent": True}]
                            }), timeout=20.0))

                            readme_tasks.append(asyncio.wait_for(self.call_child_tool_internal("octocode", "githubSearchCode", {
                                "queries": [{"owner": owner, "repo": repo, "pattern": search_keywords[0], "match": "file", "page": 1}]
                            }), timeout=20.0))

                        readmes = await asyncio.gather(*readme_tasks, return_exceptions=True)

                        combined_readmes = f"Found {len(repos)} relevant repositories. Extracted insights:\n\n"
                        for idx, (owner, repo) in enumerate(repos[:3]):
                            combined_readmes += f"### 🐙 Repository: {owner}/{repo}\n"

                            # README
                            res_readme = readmes[idx*2]
                            readme_content = ""
                            if not isinstance(res_readme, Exception):
                                readme_content = extract_text_from_result(res_readme)

                            if isinstance(res_readme, Exception) or (isinstance(res_readme, dict) and "error" in res_readme and res_readme["error"]) or "error:" in readme_content.lower() or "API Error:" in readme_content:
                                combined_readmes += f"*- README not available-*\n\n"
                            else:
                                if len(readme_content) > 1500:
                                    readme_content = readme_content[:1500] + "\n..."
                                combined_readmes += "**README Excerpt:**\n" + readme_content + "\n\n"

                            # Code Match
                            res_code = readmes[idx*2 + 1]
                            code_content = ""
                            if not isinstance(res_code, Exception):
                                code_content = extract_text_from_result(res_code)

                            if isinstance(res_code, Exception) or (isinstance(res_code, dict) and "error" in res_code and res_code["error"]) or "error:" in code_content.lower() or "API Error:" in code_content:
                                pass # Skip code if not available
                            else:
                                if len(code_content) > 1500:
                                    code_content = code_content[:1500] + "\n..."
                                combined_readmes += "**Code Snippet Matches:**\n" + code_content + "\n\n"

                        return {"tool_name": "octocode", "content": combined_readmes}
                    except Exception as e:
                        return {"tool_name": "octocode", "error": f"GitHub deep search timed out or failed: {e}"}

                return {"tool_name": "octocode", "content": "Octocode not available"}

            tasks.append(search_github_deep(query))
            source_names.append("🐙 GitHub (Repositories & Code)")

        if source in ["arxiv", "both"] and "arxiv" in self.children:
            async def search_arxiv_safe(q):
                try:
                    res = await asyncio.wait_for(self.call_child_tool_internal("arxiv", "search_papers", {
                        "query": q
                    }), timeout=45.0)
                    if isinstance(res, dict) and "error" in res and res["error"]:
                        return {"tool_name": "arxiv", "error": res["error"]}
                    
                    content_str = extract_text_from_result(res)
                    if not content_str.strip() or "error" in content_str.lower():
                        return {"tool_name": "arxiv", "content": f"No papers found or error: {content_str}"}
                        
                    return {"tool_name": "arxiv", "content": content_str}
                except Exception as e:
                    return {"tool_name": "arxiv", "error": f"arXiv search failed: {e}"}
                    
            tasks.append(search_arxiv_safe(query))
            source_names.append("📄 Academic Papers (arXiv)")
            
        if not tasks:
            await self.send_to_client({
                "jsonrpc": "2.0",
                "id": client_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: No search provider available for '{source}'."}]
                }
            })
            return
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined_text = f"# 🔍 Deep Research Insights for: {query}\n\n"
        combined_text += "> **Research Objective:** Extract clear, actionable architectural insights from multiple domains to synthesize the optimal solution.\n\n"
        
        raw_insights = ""
        for idx, res in enumerate(results):
            source_name = source_names[idx] if idx < len(source_names) else f"Source {idx}"
            combined_text += f"## {source_name}\n"
            if isinstance(res, Exception):
                combined_text += f"*Error from source: {res}*\n\n"
                continue
            
            tool_res = res
            content_str = extract_text_from_result(tool_res)
                
            # If the content is extremely large, truncate it for raw_insights but keep full for combined_text
            raw_insights += f"Source {source_name}:\n{content_str[:5000]}\n\n"
            combined_text += content_str + "\n\n---\n\n"

        # Try to use ShopAPI LLM to synthesize if possible
        import os
        from urllib import request, error
        import json as builtin_json
        
        api_key = os.environ.get("SHOPAPI_LLM_API_KEY")
        base_url = os.environ.get("SHOPAPI_BASE_URL", "https://direct.shopaikey.com/v1")
        model = os.environ.get("SHOPAPI_MODEL_LLM", "gpt-4o-mini")
        
        synthesis = ""
        if api_key:
            try:
                log("Attempting to synthesize research with ShopAPI...")
                req_data = builtin_json.dumps({
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an expert software architect. Synthesize the raw research data into a clear, actionable improvement plan. Group by 1. Core Ideas, 2. Best Practices from Github, 3. Academic/Theoretical foundations. Provide specific code strategies and avoid vague fluff."},
                        {"role": "user", "content": f"Query: {query}\n\nRaw Research:\n{raw_insights}"}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.3
                }).encode('utf-8')
                
                req = request.Request(f"{base_url}/chat/completions", data=req_data, headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                })
                
                with request.urlopen(req, timeout=30.0) as response:
                    resp_data = builtin_json.loads(response.read().decode('utf-8'))
                    synthesis = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            except Exception as e:
                log(f"Synthesis failed: {e}")
                
        if synthesis:
            combined_text = f"# 🧠 Synthesized Action Plan\n\n{synthesis}\n\n---\n\n" + combined_text
            
        # Save output to markdown file
        import time
        os.makedirs("artifacts", exist_ok=True)
        filename = f"artifacts/research_proposal_{int(time.time())}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(combined_text)
            
        hints = {
            "next_tools_to_call": [f"ctx_read('{filename}')"],
            "tools_to_avoid": ["meta_research_idea"],
            "estimated_remaining_calls": 2
        }
        
        response_content = [
            {
                "type": "text",
                "text": f"✅ Deep Research completed successfully.\n\nExtracted rich content from technical articles, cross-referenced multiple GitHub repositories (fetching READMEs and code structure), and retrieved academic papers.\n\n" + ("✨ An AI-synthesized action plan was successfully generated.\n\n" if synthesis else "") + f"The detailed research data has been saved to: `{filename}`.\n\nPlease read this file using `ctx_read('{filename}')` to evaluate the architectural approach and actionable insights for your problem."
            },
            {
                "type": "text",
                "text": f"\n\n---\n### 💡 Smart Hints\n```json\n{json.dumps(hints, indent=2, ensure_ascii=False)}\n```"
            }
        ]
        
        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": response_content
            }
        })

    def add_meta_tools_to_list(self, all_tools):
        meta_tools = [
            {
                "name": "meta_deep_context",
                "description": "ONE-STOP tool: Trả về MỌI thứ Agent cần biết về 1 symbol (context, dependencies, impact/blast radius, call chain, complexity) dựa trên intent.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol_name": {
                            "type": "string",
                            "description": "Tên của function, class, hoặc method cần phân tích."
                        },
                        "intent": {
                            "type": "string",
                            "enum": ["refactor", "rename", "debug", "understand"],
                            "description": "Mục đích phân tích để tối ưu kết quả trả về."
                        }
                    },
                    "required": ["symbol_name", "intent"]
                }
            },
            {
                "name": "meta_research_idea",
                "description": "Research tool: Search the web (blogs, articles, documentation) or arXiv for research papers to find ideas for debugging or system improvement.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query describing the bug or the system improvement idea."
                        },
                        "source": {
                            "type": "string",
                            "enum": ["web", "arxiv", "both"],
                            "description": "Where to search for ideas. Use 'web' for blogs/docs, 'arxiv' for academic papers, or 'both' (default is 'both')."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "meta_explore_structure",
                "description": "Exploration tool: Gộp tìm kiếm ngữ nghĩa, quét thư mục và đọc cấu trúc file để trả về sơ đồ các file và hàm khớp với query.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa tìm kiếm (hàm, biến, hoặc mô tả nghiệp vụ)."
                        },
                        "target_dir": {
                            "type": "string",
                            "description": "Thư mục giới hạn quét (mặc định là root)."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "meta_safe_edit_preview",
                "description": "Refactoring Safeguard tool: Xem trước chỉnh sửa an toàn bằng cách lấy định nghĩa symbol, phân tích blast radius thượng nguồn (upstream impact) và tìm các test file liên quan.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol_name": {
                            "type": "string",
                            "description": "Tên function/class dự định sửa."
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Đường dẫn file chứa symbol đó."
                        }
                    },
                    "required": ["symbol_name", "file_path"]
                }
            },
            {
                "name": "meta_trace_flow",
                "description": "Debugging & Tracing tool: Hỗ trợ debug nhanh bằng cách lấy body của symbol, độ phức tạp cyclomatic, danh sách callers và các test case tương ứng.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "error_symbol": {
                            "type": "string",
                            "description": "Tên symbol gây lỗi hoặc cần trace dòng chảy."
                        }
                    },
                    "required": ["error_symbol"]
                }
            },
            {
                "name": "visual_start_chart_server",
                "description": "Khởi tạo HTTP server nội trú tại port 3000 phục vụ thư mục chứa file biểu đồ .html. Chỉ bật khi có yêu cầu sử dụng sub-agent.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Thư mục phục vụ file (mặc định 'artifacts/charts')."
                        }
                    }
                }
            },
            {
                "name": "visual_playwright_screenshot",
                "description": "Dùng Playwright mở headless browser truy cập http://localhost:3000/{filename}, chụp screenshot toàn bộ trang và trả về ảnh dạng chuỗi Base64.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Tên file html biểu đồ cần chụp (ví dụ: 'chart_1782189356.html')."
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "visual_extract_dom_boxes",
                "description": "Trích xuất DOM Bounding Box của các nhãn trên trục X/Y, legend, title để xác định tình trạng chồng chéo (overlap).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Tên file html biểu đồ cần kiểm tra (ví dụ: 'chart_1782189356.html')."
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "visual_check_wcag_contrast",
                "description": "Nhận thông tin mã màu (hoặc trích xuất từ phần tử DOM) và tính toán tỷ lệ tương phản theo công thức WCAG 2.x, trả về đánh giá đạt/không đạt.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text_color": {
                            "type": "string",
                            "description": "Mã màu chữ (hex hoặc rgb, ví dụ: '#ffffff' hoặc 'rgb(255,255,255)')."
                        },
                        "bg_color": {
                            "type": "string",
                            "description": "Mã màu nền (hex hoặc rgb, ví dụ: '#000000' hoặc 'rgb(0,0,0)')."
                        }
                    },
                    "required": ["text_color", "bg_color"]
                }
            }
        ]
        all_tools.extend(meta_tools)

    async def handle_meta_explore_structure(self, client_id, arguments):
        query = arguments.get("query")
        target_dir = arguments.get("target_dir", ".")
        log(f"Handling meta_explore_structure for query={query} in target_dir={target_dir}")
        
        tasks = []
        if "lean-ctx" in self.children:
            tasks.append(self.call_child_tool_internal("lean-ctx", "ctx_search", {"pattern": query, "path": target_dir}))
        if "codegraphcontext" in self.children:
            tasks.append(self.call_child_tool_internal("codegraphcontext", "find_code", {"query": query}))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        markdown_sections = [f"# Explore Structure for `{query}`"]
        for r in results:
            if isinstance(r, Exception) or not r or "error" in r:
                continue
            markdown_sections.append(r.get("content", ""))
            
        merged_text = "\n\n".join(markdown_sections)
        hints = self.generate_hints_for_meta(query, "understand", merged_text)
        
        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [
                    {"type": "text", "text": merged_text},
                    {"type": "text", "text": f"\n\n---\n### 💡 Smart Hints\n```json\n{json.dumps(hints, indent=2, ensure_ascii=False)}\n```"}
                ]
            }
        })

    async def handle_meta_safe_edit_preview(self, client_id, arguments):
        symbol_name = arguments.get("symbol_name")
        file_path = arguments.get("file_path")
        log(f"Handling meta_safe_edit_preview for symbol_name={symbol_name} in file_path={file_path}")
        
        tasks = []
        if "gitnexus" in self.children:
            tasks.append(self.call_child_tool_internal("gitnexus", "impact", {"target": symbol_name, "direction": "upstream", "summaryOnly": True}))
        if "lean-ctx" in self.children:
            tasks.append(self.call_child_tool_internal("lean-ctx", "ctx_read", {"path": file_path, "mode": "signatures"}))
            tasks.append(self.call_child_tool_internal("lean-ctx", "ctx_search", {"pattern": symbol_name, "path": "test"}))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        markdown_sections = [f"# Safe Edit Preview for `{symbol_name}` in `{file_path}`"]
        for r in results:
            if isinstance(r, Exception) or not r or "error" in r:
                continue
            markdown_sections.append(r.get("content", ""))
            
        merged_text = "\n\n".join(markdown_sections)
        hints = self.generate_hints_for_meta(symbol_name, "refactor", merged_text)
        
        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [
                    {"type": "text", "text": merged_text},
                    {"type": "text", "text": f"\n\n---\n### 💡 Smart Hints\n```json\n{json.dumps(hints, indent=2, ensure_ascii=False)}\n```"}
                ]
            }
        })

    async def handle_meta_trace_flow(self, client_id, arguments):
        error_symbol = arguments.get("error_symbol")
        log(f"Handling meta_trace_flow for error_symbol={error_symbol}")
        
        tasks = []
        if "codegraphcontext" in self.children:
            tasks.append(self.call_child_tool_internal("codegraphcontext", "analyze_code_relationships", {"target": error_symbol, "query_type": "find_callers"}))
            tasks.append(self.call_child_tool_internal("codegraphcontext", "calculate_cyclomatic_complexity", {"function_name": error_symbol}))
        if "gitnexus" in self.children:
            tasks.append(self.call_child_tool_internal("gitnexus", "context", {"name": error_symbol}))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        markdown_sections = [f"# Trace Flow analysis for `{error_symbol}`"]
        for r in results:
            if isinstance(r, Exception) or not r or "error" in r:
                continue
            markdown_sections.append(r.get("content", ""))
            
        merged_text = "\n\n".join(markdown_sections)
        hints = self.generate_hints_for_meta(error_symbol, "debug", merged_text)
        
        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [
                    {"type": "text", "text": merged_text},
                    {"type": "text", "text": f"\n\n---\n### 💡 Smart Hints\n```json\n{json.dumps(hints, indent=2, ensure_ascii=False)}\n```"}
                ]
            }
        })

    async def handle_visual_start_chart_server(self, client_id, arguments):
        directory = arguments.get("directory", "artifacts/charts")
        log(f"Handling visual_start_chart_server for directory={directory}")
        import threading
        import http.server
        import socketserver
        
        if self.chart_http_server is not None:
            await self.send_to_client({
                "jsonrpc": "2.0",
                "id": client_id,
                "result": {
                    "content": [{"type": "text", "text": f"HTTP Server is already running on port 3000 (Serving {directory})."}]
                }
            })
            return

        os.makedirs(directory, exist_ok=True)
        PORT = 3000
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
            def log_message(self, format, *args):
                log(f"[HTTP Server] {format%args}")

        try:
            httpd = socketserver.TCPServer(("", PORT), Handler)
            self.chart_http_server = httpd
            
            def serve_forever():
                try:
                    httpd.serve_forever()
                except Exception as e:
                    log(f"HTTP Server stopped: {e}")
                    
            threading.Thread(target=serve_forever, daemon=True).start()
            msg = f"✅ Khởi tạo thành công HTTP Server nội trú tại http://localhost:{PORT} phục vụ thư mục '{directory}'."
        except Exception as e:
            msg = f"⚠️ Không thể khởi tạo HTTP Server tại port {PORT}: {e}"

        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [{"type": "text", "text": msg}]
            }
        })

    async def handle_visual_playwright_screenshot(self, client_id, arguments):
        filename = arguments.get("filename")
        log(f"Handling visual_playwright_screenshot for filename={filename}")
        import base64
        
        url = f"http://localhost:3000/{filename}"
        base64_image = ""
        error_msg = ""
        
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                await page.wait_for_timeout(2000) # Wait for chart animations & rendering
                screenshot_bytes = await page.screenshot(full_page=True)
                base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')
                await browser.close()
        except Exception as e:
            log(f"Playwright screenshot failed: {e}")
            error_msg = str(e)

        if error_msg:
            result_data = {"error": f"Failed to capture screenshot for {url}: {error_msg}"}
        else:
            result_data = {"url": url, "base64_image": base64_image, "status": "success"}

        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result_data, indent=2, ensure_ascii=False)}]
            }
        })

    async def handle_visual_extract_dom_boxes(self, client_id, arguments):
        filename = arguments.get("filename")
        log(f"Handling visual_extract_dom_boxes for filename={filename}")
        
        url = f"http://localhost:3000/{filename}"
        bounding_boxes = []
        has_overlap = False
        error_msg = ""
        
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Extract text elements bounding boxes
                script = """() => {
                    const texts = Array.from(document.querySelectorAll('text'));
                    return texts.map(t => {
                        const rect = t.getBoundingClientRect();
                        const style = window.getComputedStyle(t);
                        return {
                            text: t.textContent.trim(),
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            color: style.color,
                            backgroundColor: style.backgroundColor,
                            fontSize: style.fontSize,
                            transform: t.getAttribute('transform') || ''
                        };
                    }).filter(item => item.text.length > 0);
                }"""
                bounding_boxes = await page.evaluate(script)
                await browser.close()
                
                # Basic overlap check heuristic on X axis items (items with roughly same Y)
                y_groups = {}
                for box in bounding_boxes:
                    y_key = round(box['y'] / 10) * 10 # Group by near Y
                    if y_key not in y_groups:
                        y_groups[y_key] = []
                    y_groups[y_key].append(box)
                
                for y_key, items in y_groups.items():
                    if len(items) > 1:
                        items.sort(key=lambda b: b['x'])
                        for i in range(len(items)-1):
                            curr = items[i]
                            nxt = items[i+1]
                            # Check horizontal overlap
                            if curr['x'] + curr['width'] > nxt['x']:
                                has_overlap = True
                                break
                    if has_overlap:
                        break
                        
        except Exception as e:
            log(f"Playwright DOM extraction failed: {e}")
            error_msg = str(e)

        if error_msg:
            result_data = {"error": f"Failed to extract DOM boxes for {url}: {error_msg}"}
        else:
            result_data = {
                "url": url,
                "total_text_elements": len(bounding_boxes),
                "has_overlap": has_overlap,
                "overlap_details": "Phát hiện nhãn trục X bị chồng chéo (overlap). Đề xuất sửa code Plotly: xoay nhãn tickangle=45 hoặc ẩn bớt nhãn." if has_overlap else "Các nhãn hiển thị rõ ràng, không bị chồng chéo.",
                "bounding_boxes": bounding_boxes
            }

        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result_data, indent=2, ensure_ascii=False)}]
            }
        })

    async def handle_visual_check_wcag_contrast(self, client_id, arguments):
        text_color = arguments.get("text_color", "#ffffff").strip()
        bg_color = arguments.get("bg_color", "#000000").strip()
        log(f"Handling visual_check_wcag_contrast for text={text_color}, bg={bg_color}")
        
        def parse_color(c):
            c = c.lower().strip()
            if c.startswith("rgb"):
                import re
                vals = re.findall(r"\d+", c)
                if len(vals) >= 3:
                    return int(vals[0]), int(vals[1]), int(vals[2])
            elif c.startswith("#"):
                c = c.lstrip("#")
                if len(c) == 3:
                    c = "".join([x*2 for x in c])
                if len(c) == 6:
                    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            # Default fallback
            return 0, 0, 0

        def get_luminance(r, g, b):
            a = [x / 255.0 for x in (r, g, b)]
            a = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in a]
            return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]

        r1, g1, b1 = parse_color(text_color)
        r2, g2, b2 = parse_color(bg_color)
        
        l1 = get_luminance(r1, g1, b1)
        l2 = get_luminance(r2, g2, b2)
        
        if l1 < l2:
            l1, l2 = l2, l1
            
        contrast = (l1 + 0.05) / (l2 + 0.05)
        
        normal_pass = contrast >= 4.5
        large_pass = contrast >= 3.0
        
        result_data = {
            "text_color": text_color,
            "bg_color": bg_color,
            "contrast_ratio": round(contrast, 2),
            "normal_text_wcag_pass": normal_pass,
            "large_text_wcag_pass": large_pass,
            "evaluation": "Đạt chuẩn WCAG 2.x (Độ tương phản tốt, dễ đọc)." if normal_pass else ("Chỉ đạt chuẩn cho text lớn (>=18pt hoặc bold >=14pt)." if large_pass else "⚠️ Không đạt chuẩn WCAG (Độ tương phản quá thấp, khó đọc). Đề xuất thay đổi màu nền hoặc màu chữ.")
        }

        await self.send_to_client({
            "jsonrpc": "2.0",
            "id": client_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result_data, indent=2, ensure_ascii=False)}]
            }
        })

    async def call_child_tool_internal(self, child_name, tool_name, arguments):
        """Helper to invoke a tool internally and return the text result."""
        internal_id = self.next_internal_id
        self.next_internal_id += 1
        
        fut = asyncio.get_running_loop().create_future()
        req_key = f"internal_call:{internal_id}"
        self.pending_requests[req_key] = fut
        
        child = self.children[child_name]
        await child.send({
            "jsonrpc": "2.0",
            "id": f"{child.name}:internal_call:{internal_id}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        })
        
        try:
            # Wait for response with a longer timeout
            res = await asyncio.wait_for(fut, timeout=180.0)
            text_content = ""
            for item in res.get("content", []):
                if item.get("type") == "text":
                    text_content += item.get("text", "")
            return {"tool_name": tool_name, "content": text_content}
        except asyncio.TimeoutError:
            log(f"Internal call to {tool_name} timed out.")
            return {"tool_name": tool_name, "error": "Timeout after 180 seconds"}
        except Exception as e:
            log(f"Internal call to {tool_name} failed: {e}")
            return {"tool_name": tool_name, "error": str(e)}
        finally:
            self.pending_requests.pop(req_key, None)

    def inject_smart_hints(self, child_name, id_str, result):
        """Parse response content and append _agent_hint block to guide the agent."""
        content = result.get("content", [])
        if not content:
            return result

        # Extract text content
        text_content = ""
        for item in content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        # Find tool name from id_str or trace
        # Try to parse next tools dynamically based on output
        next_tools = []
        avoid_tools = []
        remaining_calls = 3

        # Parse file paths
        file_paths = list(set(re.findall(r"(?:src|test|app|data)/[a-zA-Z0-9_\-/]+\.(?:py|json|ipynb|md|js|ts|ini)", text_content)))
        
        # Basic heuristic logic
        if "context" in id_str or "find_code" in id_str:
            if file_paths:
                next_tools = [f"ctx_read('{f}')" for f in file_paths[:2]]
                avoid_tools = ["ctx_search", "find_code"]
                remaining_calls = 2
            else:
                next_tools = ["ctx_search"]
                remaining_calls = 4
        elif "ctx_search" in id_str:
            if file_paths:
                next_tools = [f"ctx_read('{f}')" for f in file_paths[:2]]
                avoid_tools = ["ctx_search"]
                remaining_calls = 2
            else:
                next_tools = ["ctx_search"]
                remaining_calls = 3
        elif "ctx_read" in id_str:
            next_tools = ["ctx_edit", "ctx_shell"]
            avoid_tools = ["ctx_read"]
            remaining_calls = 1
        else:
            # Fallback
            if file_paths:
                next_tools = [f"ctx_read('{f}')" for f in file_paths[:2]]
                avoid_tools = ["ctx_search"]
            else:
                next_tools = ["ctx_read", "ctx_search"]

        # Formulate hint JSON
        hint_dict = {
            "next_tools_to_call": next_tools,
            "tools_to_avoid": avoid_tools,
            "estimated_remaining_calls": remaining_calls
        }

        # Try to embed into JSON response if output is pure JSON
        is_json = False
        try:
            parsed = json.loads(text_content.strip())
            if isinstance(parsed, dict):
                parsed["_agent_hint"] = hint_dict
                # Replace the text item
                for item in content:
                    if item.get("type") == "text":
                        item["text"] = json.dumps(parsed, indent=2, ensure_ascii=False)
                        is_json = True
                        break
        except:
            pass

        if not is_json:
            # Append markdown hints block
            hint_str = f"\n\n---\n### 💡 Smart Hints\n```json\n{json.dumps(hint_dict, indent=2, ensure_ascii=False)}\n```"
            # Append to the last text block or create a new one
            last_text_item = None
            for item in reversed(content):
                if item.get("type") == "text":
                    last_text_item = item
                    break
            if last_text_item:
                last_text_item["text"] += hint_str
            else:
                content.append({"type": "text", "text": hint_str})

        return result

    def generate_hints_for_meta(self, symbol_name, intent, output_text):
        file_paths = list(set(re.findall(r"(?:src|test|app|data)/[a-zA-Z0-9_\-/]+\.(?:py|json|ipynb|md|js|ts|ini)", output_text)))
        next_tools = []
        avoid = ["context", "find_code", "impact"]
        
        if intent in ["refactor", "rename"]:
            if file_paths:
                next_tools = [f"ctx_read('{f}')" for f in file_paths[:2]]
            else:
                next_tools = ["ctx_search"]
            remaining = 3
        elif intent == "debug":
            if file_paths:
                next_tools = [f"ctx_read('{f}')" for f in file_paths[:2]] + ["ctx_shell"]
            else:
                next_tools = ["ctx_search"]
            remaining = 4
        else: # understand
            if file_paths:
                next_tools = [f"ctx_read('{f}')" for f in file_paths[:2]]
            else:
                next_tools = ["ctx_search"]
            remaining = 1

        return {
            "next_tools_to_call": next_tools,
            "tools_to_avoid": avoid,
            "estimated_remaining_calls": remaining
        }

async def run_server():
    server = MetaMCPServer()
    try:
        await server.start()
    finally:
        await server.stop()

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        log("Server stopped by user interrupt")
    except Exception as e:
        log(f"Server crashed: {e}\n{traceback.format_exc()}")
