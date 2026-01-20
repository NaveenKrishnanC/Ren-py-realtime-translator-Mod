init -999 python:
    
    def init_persistent_var(var_name, default_value):
            if (not hasattr(persistent, var_name)) or (getattr(persistent, var_name) is None) or (not SCREEN_CONFIG):
                setattr(persistent, var_name, default_value)
    global SCREEN_CONFIG,TRANSLATION_PROMPT
    SCREEN_CONFIG = True
    persistent_vars = [
        ("enable_translation", False),# Default: False to disable translation
        ("show_comparison", False),# Default: False to only display translated text.True to display both original and translated text
        ("target_language", "de"),# Default: "de" for German, change it to your target language ISO 639-1 code
        ("translation_service", "google"),# Default: "google", "bing",or "LLM","freellm"is supported now,if you use "auto",service will perform in turn on google-bing-freellm
        
        ("time_interval", 0.05),# Default: 0.05 seconds interval between translation API requests for google and bing,1.5 seconds is recommended for llm and freellm.
        ("redraw_time",0.02), #Default:0.02 seconds interval between redraw texts,if you are using this mod in Android or Old pc,you should set it higher
        ("trans_font", "GoNotoCurrent-Regular.ttf"),# Default: "GoNotoCurrent-Regular.ttf", change it to your desired font name,and make sure the font file is in the "game" folder
        ("glossary_enabled", False),# Default: False to disable glossary replacement
        ("x_button_pos", 1.0),# Default: 1.0  for button on the right of the screen
        ("y_button_pos", 0.05),# Default:0.05 for button on the top of the screen
        ("save_interval", 30),# Default:every 30 seconds to save translation_cache
        ("llm_maxtexts", 30),# Default: 30 texts sent to translate for freellm and llm in one requests
        ("normal_maxtexts", 100),# Default: 100 texts sent to translate for google and bing in one requests
        
        ("api_keys", ["Your-API-KEY1", "Your-API-KEY2"]),#api,model,keys can not be set within the game ,you need to edit this file to change them.
        ("model_name", "meta-llama/llama-3.3-8b-instruct:free"),
        ("base_url", "https://openrouter.ai/api/v1/chat/completions"),
        ("max_tokens", 8000),#max tokens for llm response
        ("temperature", 0.05),# temperature means the degree of randomness of the model's output
        ("timeout", 60),# Default: 60 seconds timeout for translation API requests
        ("appended_lines", 10),# Default: 10 lines of contexts to append for translation

        ("proxies", {} ),#proxies can not be set within the games ,you need to edit this file to change them.
        ("proxies_enabled", False),# Default: False to disable proxies

        ("font_size_adjustment_enabled", False),# Default: False to disable font size adjustment
        ("font_size_adjustment_min_scale", 0.5),# Default: 0.5 means minimum  size is 50% of original size
        ("font_size_adjustment_max_scale", 2.0),# Default: 2.0 means maximum size is 200% of original size
        ("font_size_adjustment_length_threshold", 1.5),# Default: 1.5 means if translated text is 150% longer than original text or 50% shorter,  size adjustment will be applied

        ("enable_rtl", False),# Default: False to disable RTL (Right-to-Left) text support
        
        ("last_saved_cache_size", 0),
        ("PRESCAN_FLAG", 0)
    ]
    
    for var_name, default_value in persistent_vars:
        init_persistent_var(var_name, default_value)
    if not hasattr(persistent, "display_translation") or persistent.display_translation is None or not SCREEN_CONFIG:
        persistent.display_translation = persistent.enable_translation

    TRANSLATION_PROMPT = r"""You are a professional game localization expert. Please translate the following renpy game text from English to {target_lang}.
                        Translation requirements:
                        1. Maintain game terminology consistency
                        2. Preserve all HTML tags, format codes and special marks 
                        3. Special attention: The text may contain <code id="...">...</code> tags. The content inside these tags must not be changed under any circumstances and must be preserved as is.
                        4. Maintain the natural fluency of game dialogue
                        5. Adapt to the personality characteristics of game characters
                        6. Preserve all programming-related symbols (such as %variable%, [option], etc.)

                        Previously texts for reference:
                        {context}

                        Please translate the following content:"""
    def trans_init():
        
        global REQUESTS_AVAILABLE,TRANSLATION_CACHE_FILE,PENDING_TRANSLATIONS
        global LAST_TRANSLATION_TIME,LAST_REDRAW_TIME
        global GLOSSARY_FILE,LAST_SAVE_TIME
        global glossary_dic,sorted_glossary_terms
        global tag_pattern,escape_pattern,percent_pattern,brace_pattern,escaped_char_pattern
        global bracket_pattern,link_pattern,img_pattern,input_pattern
        global source_pattern,comhtml_to_text_pattern
        global aria_token_nums,aria_access_token
        global methods,reverse_methods,auto_service_index,retry_methods,reverse_retry_methods
        global latest_font,font_groups,main_font,emoji_font
        global api_index,max_api_index
        global var_texts_dict, var_pattern         
    
        try:
            import requests
            REQUESTS_AVAILABLE = True
        except ImportError:
            import urllib2
            REQUESTS_AVAILABLE = False
        
        import re
        var_pattern = re.compile(r'\[([^\[\]]+)\]') 
        var_texts_dict = {}
        TRANSLATION_CACHE_FILE = "translation_cache.json"
        PENDING_TRANSLATIONS = set()
        LAST_TRANSLATION_TIME = 0
        LAST_REDRAW_TIME=0
        
        glossary_dic={}
        GLOSSARY_FILE="glossary.json"
        LAST_SAVE_TIME=0
        
        aria_access_token=0
        aria_token_nums=0
        escaped_char_pattern = re.compile(r'''
        \\ (u[0-9a-fA-F]{4}| U[0-9a-fA-F]{8}| x[0-9a-fA-F]{2}| [0-7]{1,3} )
        ''', re.VERBOSE)
        tag_pattern = re.compile(r'(\s*\{[^}]*\}\s*)')
        comhtml_to_text_pattern = re.compile(r'<div id="(\d+)"[^>]*>(.*?)</div>', re.DOTALL)  
        escape_pattern = re.compile(r'\\(.)')
        percent_pattern = re.compile(r'(%(?:(?:\d+|\*)?(?:\.(?:\d+|\*))?[#0\-+]?[hlL]?[bdiouxXeEfFgGcrsaHMSpTtn]|%))')
        brace_pattern = re.compile(r'(\{[^{}]*\{?[^{}]*\}?[^{}]*\})')
        bracket_pattern = re.compile(r'(\[{1,2}.*?\])')
        link_pattern = re.compile(r'<link rel="(.*?)"/>')
        img_pattern = re.compile(r'<img src="(.*?)"/>')
        source_pattern = re.compile(r'<source src="(.*?)"/>')
        input_pattern = re.compile(r"<input type='(.*?)'/>") 
        methods={0: "google",1: "bing",2: "freellm",3: "LLM"}
        retry_methods={0: "google",1: "bing"}
        reverse_methods = {value: key for key, value in methods.items()}
        reverse_retry_methods = {value: key for key, value in retry_methods.items()}
        auto_service_index=0
        latest_font = "None"
        font_groups = {}
        main_font = persistent.trans_font
        emoji_font = "TwemojiCOLRv0.ttf"
        
        api_index = 0
        max_api_index=len(persistent.api_keys)

    def load_translation_cache():
         
        import json
        try:
            try:
                with open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as f:
                        raw_cache = json.load(f)
                
            except:
                import codecs
                with codecs.open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as f:
                        raw_cache  = json.load(f)
            mdata.translation_cache = {}
            for key, value in raw_cache.items():
                if key != value:  
                    mdata.translation_cache[key] = value
                    mdata.translated_set.add(value)
            
            persistent.last_saved_cache_size = len(mdata.translation_cache)

        except :
            mdata.translation_cache = {}
            persistent.last_saved_cache_size = 0
        try:
            renpy.save_persistent()
            global sorted_glossary_terms
            global glossary_dic
            if persistent.PRESCAN_FLAG==0:
                    if persistent.glossary_enabled:
                        try:
                            with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
                                    glossary_dic = json.load(f)
                        except:
                            import codecs
                            with codecs.open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
                                    glossary_dic = json.load(f)
                        sorted_glossary_terms = sorted(glossary_dic.keys(), key=len, reverse=True)
                    renpy.invoke_in_thread(prerun)
                    persistent.PRESCAN_FLAG=1
                    renpy.save_persistent()
        except Exception as e:
            print("Error saving persistent data:", str(e))
        
        return
    
    def safe_predict(tl):
        try:
            return tl.predict()[0]
        except Exception as e:
            print("Failed to predict:", e)
            return None
    
    def process_say_node(node):
        try:
            text_content = node.what
            if node.who is not None:
                try:
                    chara = renpy.ast.eval_who(node.who)
                    text_content = chara.prefix_suffix("what", chara.what_prefix, text_content, chara.what_suffix)
                except Exception as e:
                    pass
            if ((text_content not in mdata.translation_cache) and 
                (text_content not in mdata.PRESCAN_TEXTS) and 
                (len(text_content) > 1)):
                mdata.PRESCAN_TEXTS.add(text_content)
                variables = var_pattern.findall(text_content)
                if variables:
                    for var_name in variables:
                        if var_name not in var_texts_dict:
                            var_texts_dict[var_name] = []
                        var_texts_dict[var_name].append(text_content)
                        
        except Exception as e:
            print("Error processing say node",e)
    
    def process_menu_text(text):
        try:
            if isinstance(text, str) or isinstance(text, basestring):
                return text
            elif isinstance(text, tuple):
                if text and isinstance(text[0], str):
                    return text[0]
            elif hasattr(text, 'expression'):
                try:
                    result = renpy.python.py_eval(text.expression)
                    if isinstance(result, str):
                        return result
                except:
                    pass
            elif hasattr(text, 'w'):
                return text.w
        except:
            pass
        return ""
    
    def extract_variables_from_text(text):
        if not text:
            return
        variables = var_pattern.findall(text)
        if variables:
            for var_name in variables:
                if var_name not in var_texts_dict:
                    var_texts_dict[var_name] = []
                var_texts_dict[var_name].append(text)
    
    def process_menu_node(node):
        try:
            if hasattr(node,'title'):
                if node.title is not None:
                    title_text = process_menu_text(node.title)
                    if title_text and ((title_text not in mdata.translation_cache) and  (title_text not in mdata.PRESCAN_TEXTS) and (len(title_text) > 1)):
                        
                        mdata.PRESCAN_TEXTS.add(title_text)
                        extract_variables_from_text(title_text)

            for item in node.items:
                if len(item) >= 3:
                    label = item[0]  
                    label_text = process_menu_text(label)
                    
                    if label_text and ((label_text not in mdata.translation_cache) and (label_text not in mdata.PRESCAN_TEXTS) and  (len(label_text) > 1)):
                        
                        mdata.PRESCAN_TEXTS.add(label_text)
                        extract_variables_from_text(label_text)
        
        except Exception as e:
            print("Error processing menu node: ",e)
    


    def find_menus_in_statement(stmt, collected_menus):
        if isinstance(stmt, renpy.ast.Menu):
            collected_menus.append(stmt)
        
        if hasattr(stmt, 'block') and stmt.block:
            if isinstance(stmt.block, (list, tuple)):
                for sub_stmt in stmt.block:
                    if sub_stmt:
                        find_menus_in_statement(sub_stmt, collected_menus)
        if hasattr(stmt, 'entries') and stmt.entries:
            for entry in stmt.entries:
                if hasattr(entry, 'block') and entry.block:
                    for sub_stmt in entry.block:
                        if sub_stmt:
                            find_menus_in_statement(sub_stmt, collected_menus)

    def collect_all_menu_nodes():
        all_menu_nodes = []
        for name, item in renpy.game.script.namemap.items():
            if isinstance(item, (renpy.ast.Label, renpy.ast.Translate)):
                find_menus_in_statement(item, all_menu_nodes)
        
        return all_menu_nodes

    def prerun():
        import time
        
        try:
            _renpy_translator = renpy.game.script.translator
            time.sleep(0.1)
            print("Starting pre-scan at time: ", renpy.time.time())
            all_nodes = []
            print("Collecting nodes from translate objects...")
            for tl in _renpy_translator.default_translates.values():
                node = safe_predict(tl)
                if node:
                    all_nodes.append(node)
            print("Collecting nodes via AST parsing...")
            all_menu_nodes = collect_all_menu_nodes()
            all_nodes.extend(all_menu_nodes)
            print("Collecting additional nodes...")
            for name, node in renpy.game.script.namemap.items():
                if isinstance(node, renpy.ast.Say) and node not in all_nodes:
                    all_nodes.append(node)
                elif isinstance(node, renpy.ast.Menu) and node not in all_nodes:
                    all_nodes.append(node)
            all_nodes = list(set(filter(None, all_nodes)))
            all_nodes.sort(key=lambda n: (n.filename, n.linenumber) if hasattr(n, 'filename') and hasattr(n, 'linenumber') else ("", 0))
            
            text_len = len(all_nodes)
            print(text_len, " objects to pre-scan (including menus)")
            print("Prescan thread is started.")
            say_count = 0
            menu_count = 0
            processed_count = 0
            
            for counter, node in enumerate(all_nodes):
                if isinstance(node, renpy.ast.Say):
                    process_say_node(node)
                    say_count += 1
                    processed_count += 1
                elif isinstance(node, renpy.ast.Menu):
                    process_menu_node(node)
                    menu_count += 1
                    processed_count += 1
                if counter % 200 == 0 and counter > 0:
                    print("Pre-scanned ",counter)

            print("\n" + "="*50)
            print("Pre-scan complete!")
            mdata.prescan_texts = list(mdata.PRESCAN_TEXTS)
            print("prescan_texts len is ",len(mdata.prescan_texts))
            print("="*50)
            
        except Exception as e:
            print("Error during pre-scan: ",e)
    

    def save_translation_cache():
        import json
        try:
            current_size = len(mdata.translation_cache)
            if persistent.enable_translation and persistent.display_translation :
                if  current_size >= persistent.last_saved_cache_size:
                    if current_size - persistent.last_saved_cache_size >= 1 :
                        try:
                            with open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
                                json.dump(mdata.translation_cache, f, ensure_ascii=False, indent=2)
                        except:
                            import codecs
                            with codecs.open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
                                json.dump(mdata.translation_cache, f, ensure_ascii=False, indent=2)
                        persistent.last_saved_cache_size = max(current_size, persistent.last_saved_cache_size)
                        renpy.save_persistent()
                        return True
                    else:
                        return False

                else:
                    print("Translation cache size decreased, reloading cache...")
                    load_translation_cache()
                    return False
        except:
            return False

    
    def add_text_object_to_redraw(text_content, text_obj):
            if text_content not in mdata.TEXT_OBJECTS_TO_REDRAW:
                mdata.TEXT_OBJECTS_TO_REDRAW[text_content] = set()
            mdata.TEXT_OBJECTS_TO_REDRAW[text_content].add(text_obj)
    def get_text_objects_for_redraw(text_content):
        if text_content in mdata.TEXT_OBJECTS_TO_REDRAW:
            obj_set = mdata.TEXT_OBJECTS_TO_REDRAW[text_content]
            return list(obj_set)
        return []
    def remove_text_content_from_redraw(text_content):
        if text_content in mdata.TEXT_OBJECTS_TO_REDRAW:
            del mdata.TEXT_OBJECTS_TO_REDRAW[text_content]
    def cleanup_empty_sets():
        empty_keys = [key for key, weak_set in mdata.TEXT_OBJECTS_TO_REDRAW.items() if len(weak_set) == 0]
        for key in empty_keys:
            del mdata.TEXT_OBJECTS_TO_REDRAW[key]
        short_keys= [key for key, weak_set in mdata.TEXT_OBJECTS_TO_REDRAW.items() if len(key)<3]
        for key in short_keys:
            del mdata.TEXT_OBJECTS_TO_REDRAW[key]
    def calculate_text_length_ratio(original_text, translated_text):
        
        orig_len = len(original_text)
        trans_len = len(translated_text)
        return (1+(float(trans_len) / orig_len))/2 if orig_len > 0 else 1.0

    def get_adjusted_font_size(original_text, translated_text, original_size=22):
        if not persistent.font_size_adjustment_enabled:
            return original_size
        
        ratio = calculate_text_length_ratio(original_text, translated_text)
        if ratio > persistent.font_size_adjustment_length_threshold:
            scale = max(1.0 / ratio, persistent.font_size_adjustment_min_scale)
            return int(original_size * scale)
        elif ratio < 1.0 / persistent.font_size_adjustment_length_threshold:
            scale = min(ratio, persistent.font_size_adjustment_max_scale)
            return int(original_size * scale)
        
        return original_size
    def get_texts_to_translate(PENDING_TRANSLATIONS_copy):
        import random
         
        runtime_texts = list(PENDING_TRANSLATIONS_copy)     
        runtime_count = len(runtime_texts)
        ALL_PENDING_FLAG=0
        try:
            if len(mdata.prescan_texts)==0:
                ALL_PENDING_FLAG=1
            if persistent.translation_service == "freellm" or persistent.translation_service == "LLM":
                max_texts = persistent.llm_maxtexts+random.randint(0, 5)
            else:
                max_texts=persistent.normal_maxtexts
            if runtime_count >= max_texts:
                ALL_PENDING_FLAG=1
            texts_to_translate = runtime_texts
            if ALL_PENDING_FLAG==0:
                remaining = max_texts - runtime_count
                if remaining>0 :
                    if len(mdata.prescan_texts) > remaining:
                        selected_prescan = mdata.prescan_texts[:remaining]
                        mdata.prescan_texts=mdata.prescan_texts[remaining:]
                        texts_to_translate.extend(selected_prescan)
                    else:
                        texts_to_translate.extend(mdata.prescan_texts)
                        mdata.prescan_texts=[]
            texts_to_translate_final=[]
            for text in texts_to_translate:
                if (text not in mdata.translation_cache) and (text not in mdata.sent_set_twice):
                    
                    texts_to_translate_final.append(text)
                if ((text in mdata.sent_set) and (text not in mdata.sent_set_twice)):
                    mdata.sent_set_twice.add(text)
                mdata.sent_set.add(text)
            return texts_to_translate_final
        except Exception as e:
            print("get_texts_to_translate error",e)
            return runtime_texts
    def translation_thread(texts_to_translate,translation_service0=persistent.translation_service):
        for failed_times in range(5):
            if failed_times>0:
                if failed_times>3:
                    print("all method failed")
                    return 
                else:
                    translation_service=retry_methods[(reverse_methods[translation_service0]+failed_times)%2]
                    print("current translation_service is ",translation_service,failed_times,translation_service0 )
            else:
                translation_service=translation_service0
            try:
                translations = translate_batch(texts_to_translate, persistent.target_language,translation_service) 
            except:
                continue
            if translations!= texts_to_translate:
                break
        process_translation_results(texts_to_translate, translations)
    def get_proxies():
        return persistent.proxies if persistent.proxies_enabled else None
    def _send_batch_translation_request_requests(html_content, target_lang):
        import random
        api_key = "AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520"
        url = "https://translate-pa.googleapis.com/v1/translateHtml"
        
        headers = {
            "Accept": "/",
            "Content-Type": "application/json+protobuf",
            "User-Agent": random.choice(USER_AGENTS),
            "X-Goog-API-Key": api_key,
            "model": "nmt",
            "priority":"u=1, i"
        }
        data = [
            [html_content, "auto", target_lang],
            "wt_lib"
        ]

        session = session_manager.get_session()

        response = session.post(
            url, 
            headers=headers, 
            json=data,
            proxies=session_manager._current_proxies,
            timeout=20,
        )
        response.raise_for_status()
        
        result = response.json()
        return result[0][0]
    
    def _send_batch_translation_request_urllib2(html_content, target_lang):
        import json
        import random
        import urllib2
        api_key = "AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520"
        url = "https://translate-pa.googleapis.com/v1/translateHtml"
        
        headers = {
            "Accept": "/",
            "Content-Type": "application/json+protobuf",
            "User-Agent": random.choice(USER_AGENTS),
            "X-Goog-API-Key": api_key,
            "model": "nmt",
            "priority":"u=1, i"
        }
        
        data = [
            [html_content, "auto", target_lang],
            "wt_lib"
        ]
        
        req = urllib2.Request(url, json.dumps(data), headers)
        
        if persistent.proxies_enabled:
            proxy_handler = urllib2.ProxyHandler(persistent.proxies)
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        else:
            urllib2.install_opener(urllib2.build_opener())
        
        try:
            response = urllib2.urlopen(req, timeout=20)
            result = json.loads(response.read())
            return result[0][0]
        except Exception as e:
            print("Request failed: {}".format(str(e)))
            raise
    def format_prompt(messages, add_special_tokens=False, do_continue=False, include_system=True):
            def to_string(value):
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict):
                    if "text" in value:
                        return value.get("text", "")
                    return ""
                elif isinstance(value, list):
                    result = ""
                    for v in value:
                        result += to_string(v)
                    return result
                elif value is None:
                    return ""
                else:
                    return str(value)
            if not add_special_tokens and len(messages) <= 1:
                if messages and "content" in messages[0]:
                    return to_string(messages[0]["content"])
                return ""
            processed_messages = []
            for message in messages:
                if "role" in message and "content" in message:
                    if include_system or message.get("role") != "system":
                        content_str = to_string(message["content"])
                        if content_str and content_str.strip():
                            processed_messages.append((message["role"], content_str))
            if not processed_messages:
                return ""
            formatted_parts = []
            for role, content in processed_messages:
                role_capitalized = role.capitalize()
                formatted_parts.append("{role}: {content}".format(role=role_capitalized, content=content))
            
            formatted = "\n".join(formatted_parts)
            
            if do_continue:
                return formatted
            
            return formatted + "\nAssistant:"
    def get_previous_dialogue():
        previous_dialogue = []      
        
        for h in _history_list[-persistent.appended_lines:]:             
            try:
                dialogues_content="{0}:{1}".format(h.who,h.what)
                previous_dialogue.append(dialogues_content)
            except:
                pass
        return previous_dialogue
    
    def translate_with_freellm_requests(texts, target_lang):
        import uuid
        context_items = []
        if mdata.translation_cache:
            recent_items = list(mdata.translation_cache.items())[-persistent.appended_lines:]
            for original, translated in recent_items:
                context_items.append("Original: {}\nTranslated: {}".format(original, translated))
            previous_dialogues=get_previous_dialogue()
            if previous_dialogues:
                if (len(previous_dialogues)>=persistent.appended_lines):
                    context_items=previous_dialogues
            
        
        context = "\n\n".join(context_items) if context_items else "No previous translation context available"
        prompt = TRANSLATION_PROMPT.format(target_lang=target_lang, context=context)
        combined_html = text_to_comhtml(texts)
        
        import string
        import random
        import json
        userid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(21))
        urlindex=random.randint(0,1)
        urls=[
            "https://netwrck.com/api/chatpred_or",
            "https://api.deepai.org/hacking_is_a_serious_crime",
            ]
        models=[
        [
        "thedrummer/valkyrie-49b-v1",
        "thedrummer/skyfall-36b-v2",
        "sao10k/l3-euryale-70b",
        "deepseek/deepseek-chat",
        "deepseek/deepseek-r1",
        "gryphe/mythomax-l2-13b",
        "nvidia/llama-3.1-nemotron-70b-instruct",
    ],

        ["standard", 
        "online",
        "deepseek-v3.2",
        "gemini-2.5-flash-lite",
        "qwen3-30b-a3b",
        "gpt-5-nano",
        "gpt-oss-120b",
        "llama-4-scout",
        "llama-3.3-70b-instruct",
        "gemini-2.5-pro",],
        ]
        headers=[{
            'authority': 'netwrck.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://netwrck.com',
            'referer': 'https://netwrck.com/',
            'user-agent': random.choice(USER_AGENTS),
        },
                {
            "Content-Type": "application/x-www-form-urlencoded",
            "api-key": "tryit-53926507126-2c8a2543c7b5638ca6b92b6e53ef2d2b",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": random.choice(USER_AGENTS),
            "DNT": "1",
            "Sec-CH-UA": '"Not/A)Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": 'Windows',
        }
        ]
        
        url=urls[urlindex]
        model=models[urlindex]
        model=random.choice(model)
        headers=headers[urlindex]
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": combined_html},
            {"role": "assistant", "content": "Sure,i will fullfill your requests:"}
        ]
        format_message=format_prompt(messages, add_special_tokens=True, do_continue=True)
        data=[{
            "query": format_message,
            "examples": [],
            "model_name": model,
        },
        {
            "chat_style": "chat",
            "chatHistory": json.dumps(messages),
            "model": model,
            "hacker_is_stinky": "very_stinky",
        }]
        data=data[urlindex]
        
        
        
        session = session_manager.get_session()
        if urlindex==1:
            cookies = {"__Host-session": uuid.uuid4().hex, '__cf_bm': uuid.uuid4().hex}
            session.cookies.update(cookies)
        try:
            if urlindex==0:

                response = session.post(
                    url,
                    data=json.dumps(data),
                    #json=data,
                    headers=headers,
                    proxies=session_manager._current_proxies,
                    timeout=persistent.timeout, 
                )     
            if urlindex==1:
                response = session.post(
                    url,
                    headers=headers,
                    data=data,
                    proxies=session_manager._current_proxies,
                    timeout=persistent.timeout,  
                )        
            if response.status_code == 200:
                
                if urlindex==0:
                    response.encoding = 'utf-8'
                    translated_html = response.text.strip()
                if urlindex==1:
                    translated_html=response.text.strip()
                translated_texts = comhtml_to_text(translated_html,texts)
                
                return translated_texts
            else:
                print(urlindex,model)
                print("API error: {0} - {1}".format(response.status_code, response.text))
                return texts
                
        except Exception as e:
            print("freellm translation error: {0}".format(str(e)))
            return texts
    def translate_with_freellm_urllib2(texts, target_lang=persistent.target_language):
        import string
        import json
        import random
        import urllib2
        import urllib
        
        context_items = []
        if mdata.translation_cache:
            recent_items = list(mdata.translation_cache.items())[-persistent.appended_lines:]
            for original, translated in recent_items:
                context_items.append("Original: {}\nTranslated: {}".format(original, translated))
            previous_dialogues=get_previous_dialogue()
            if previous_dialogues:
                if (len(previous_dialogues)>=persistent.appended_lines):
                    context_items=previous_dialogues
        
        context = "\n\n".join(context_items) if context_items else "No previous translation context available"
        
        prompt = TRANSLATION_PROMPT.format(target_lang=target_lang, context=context)
        
        combined_html = text_to_comhtml(texts)
        
        userid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(21))
        urlindex = random.randint(0, 1)
        urls=[
            "https://netwrck.com/api/chatpred_or",
            "https://api.deepai.org/hacking_is_a_serious_crime",
            ]
        models=[
        [
        "thedrummer/valkyrie-49b-v1",
        "thedrummer/skyfall-36b-v2",
        "sao10k/l3-euryale-70b",
        "deepseek/deepseek-chat",
        "deepseek/deepseek-r1",
        "gryphe/mythomax-l2-13b",
        "nvidia/llama-3.1-nemotron-70b-instruct",
    ],

        ["standard", 
        "online",
        "deepseek-v3.2",
        "gemini-2.5-flash-lite",
        "qwen3-30b-a3b",
        "gpt-5-nano",
        "gpt-oss-120b",
        "llama-4-scout",
        "llama-3.3-70b-instruct",
        "gemini-2.5-pro",],
        
        ]
        headers_dict=[{
            'authority': 'netwrck.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://netwrck.com',
            'referer': 'https://netwrck.com/',
            'user-agent': random.choice(USER_AGENTS),
        },
                {
            "Content-Type": "application/x-www-form-urlencoded",
            "api-key": "tryit-53926507126-2c8a2543c7b5638ca6b92b6e53ef2d2b",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": random.choice(USER_AGENTS),
            "DNT": "1",
            "Sec-CH-UA": '"Not/A)Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": 'Windows',
        },
        ]
        
        url=urls[urlindex]
        model=models[urlindex]
        model=random.choice(model)
        headers_dict=headers_dict[urlindex]
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": combined_html},
            {"role": "assistant", "content": "sure,i will fullfill your requests:"}
        ]
        format_message=format_prompt(messages, add_special_tokens=True, do_continue=True)
        data=[{
            "query": format_message,
            "examples": [],
            "model_name": model,
        },
        {
            "chat_style": "chat",
            "chatHistory": json.dumps(messages),
            "model": model,
            "hacker_is_stinky": "very_stinky",
        },
        ]
        data=data[urlindex]
        
        if urlindex == 0:
            request_data = json.dumps(data)
            content_type = "application/json"
        else:
            request_data = urllib.urlencode(data)
            content_type = "application/x-www-form-urlencoded"
        
        try:
            req = urllib2.Request(url, request_data)
            req.add_header("Accept", headers_dict.get("Accept", "*/*"))
            req.add_header("Content-Type", content_type)

            for key, value in headers_dict.items():
                if key not in ["Accept", "Content-Type"]:
                    req.add_header(key, value)

            if persistent.proxies_enabled and persistent.proxies:
                proxy_handler = urllib2.ProxyHandler(persistent.proxies)
                opener = urllib2.build_opener(proxy_handler)
                urllib2.install_opener(opener)
            else:
                urllib2.install_opener(urllib2.build_opener())
            
            response = urllib2.urlopen(req, timeout=persistent.timeout)
            response_data = response.read()

            if urlindex == 0:
                translated_html = response_data.strip()
            if urlindex == 1:
                try:
                    import gzip
                    import StringIO
                    buffer = StringIO.StringIO(response_data)
                    f = gzip.GzipFile(fileobj=buffer)
                    response_data = f.read()
                except Exception as e:
                    print("Gzip decompression failed: {}".format(str(e)))
                translated_html = response_data.strip()
            translated_texts = comhtml_to_text(translated_html, texts)
            return translated_texts
        except Exception as e:
            print("freeLLM translation error: {}".format(str(e)))
            return texts
    def _send_batch_translation_request_edge(texts, target_lang):
        import random
        try:
            url = "https://edge.microsoft.com/translate/translatetext?from=en&to={0}&isEnterpriseClient=true".format(target_lang)
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "Priority": "u=1, i",
                "User-Agent": random.choice(USER_AGENTS),
            }
            
            
            results = []
            if REQUESTS_AVAILABLE:
                session = session_manager.get_session()
                response = session.post(
                    url, 
                    headers=headers, 
                    json=texts,  
                    proxies=session_manager._current_proxies,
                    timeout=20,  
                )
                if response.status_code == 200:
                    result = response.json()
                    result = [item['translations'][0]['text'] for item in result]
                    return result       
                else:
                    print("Edge falied ",response.status_code,response)
            else:
                print("Edge translation not supported yet in Ren'py 7")
        except Exception as e:
            print("Request failed: {}".format(str(e)))
            raise
        except Exception as e:
            print("Edge  error: ",e)
        return texts
    def _send_batch_translation_request_edge_urllib2(texts, target_lang):
        import json
        import random
        import urllib2
        try:
            url = "https://edge.microsoft.com/translate/translatetext?from=en&to={0}&isEnterpriseClient=true".format(target_lang)
            
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "Priority": "u=1, i",
                "User-Agent": random.choice(USER_AGENTS),
            }

            request_data = texts
            req = urllib2.Request(url, json.dumps(request_data), headers)
            if persistent.proxies_enabled:
                proxy_handler = urllib2.ProxyHandler(persistent.proxies)
                opener = urllib2.build_opener(proxy_handler)
                urllib2.install_opener(opener)
            else:
                urllib2.install_opener(urllib2.build_opener())
            response = urllib2.urlopen(req, timeout=20)
            response_data = response.read()

            result = json.loads(response_data)
            translated_texts = [item['translations'][0]['text'] for item in result]
            return translated_texts
        except Exception as e:
            print("Edge translation error: {}".format(str(e)))
            return texts
    def _send_batch_translation_request(html_content, target_lang):
        if REQUESTS_AVAILABLE:
            return _send_batch_translation_request_requests(html_content, target_lang)
        else:
            return _send_batch_translation_request_urllib2(html_content, target_lang)
        
    def process_pending_translations():
        import random
        if not persistent.enable_translation:
            return
        global PENDING_TRANSLATIONS, LAST_TRANSLATION_TIME
        current_time = renpy.time.time()
        time_interval_random =persistent.time_interval+random.uniform(0, 0.02)
        if (current_time - LAST_TRANSLATION_TIME) < time_interval_random :
            return
        LAST_TRANSLATION_TIME = current_time
        
        if len(mdata.translation_cache)==0:
            load_translation_cache() 
        global var_texts_dict
        if var_texts_dict and random.randint(0, 9) == 0:  
            has_unprocessed_vars = process_variable_texts() 
        if (not PENDING_TRANSLATIONS) and (not mdata.prescan_texts):
            return
        PENDING_TRANSLATIONS_copy=PENDING_TRANSLATIONS
        PENDING_TRANSLATIONS=set()
        texts_to_translate = get_texts_to_translate(PENDING_TRANSLATIONS_copy)
        if len(texts_to_translate)==0:
            return
        if persistent.translation_service=="auto":
            global auto_service_index
            translation_service0=methods[auto_service_index]
            auto_service_index=(auto_service_index+1)%3
            renpy.invoke_in_thread(translation_thread, texts_to_translate,translation_service0)
        else:
            renpy.invoke_in_thread(translation_thread, texts_to_translate)
        
    def process_translation_results(texts_to_translate, translations):
        for original, translated in translations.items():
            try:
                translated = html_unescape(translated)
                translated = adjust_translation_spaces(original, translated)
                if (original != translated) : 
                    mdata.translation_cache[original] = translated
                    mdata.translated_set.add(translated)
                else:
                    if original not in mdata.retry_texts_set :
                        mdata.retry_texts_set.add(original)
                        PENDING_TRANSLATIONS.add(original)
                    else:
                        mdata.translation_cache[original] = translated
            except Exception as e:
                print("Error processing translation for '{0}': {1}".format(translated, str(e)))
        global LAST_SAVE_TIME
        current_time = renpy.time.time()
        if (current_time - LAST_SAVE_TIME) < persistent.save_interval :
            return
        LAST_SAVE_TIME=current_time
        cleanup_empty_sets()
        save_translation_cache()

    def process_redrawing_translations():
        if not persistent.enable_translation:
            return
        global LAST_REDRAW_TIME
        current_time = renpy.time.time()
        if (current_time - LAST_REDRAW_TIME) < persistent.redraw_time :
            return
        keys_to_process = list(mdata.TEXT_OBJECTS_TO_REDRAW.keys())    
        for original_dis in keys_to_process:
            try:
                if original_dis in mdata.translation_cache:
                    text_objs = get_text_objects_for_redraw(original_dis)    
                    if not text_objs:
                        print(original_dis,"has no obj to redraw")
                        continue                
                    for text_obj in text_objs:
                        if  text_obj is None:
                            continue
                        try:
                            if persistent.font_size_adjustment_enabled:
                                if hasattr(text_obj, 'style'):
                                    original_size = text_obj.style.size
                                    adjusted_size = get_adjusted_font_size(original_dis, mdata.translation_cache[original_dis],original_size)
                                    mdata.font_size_cache[mdata.translation_cache[original_dis]] = adjusted_size
                            text_obj.kill_layout()
                            renpy.display.render.redraw(text_obj, 0)
                            remove_text_content_from_redraw(original_dis)
                        except Exception as e:
                            print("Error: redrawing text object failed:", str(e),original_dis, text_obj)
                    
                    
            except Exception as e:
                print("redraw error",e)
            LAST_REDRAW_TIME = current_time  
    
    def adjust_translation_spaces(original, translated):
        global tag_pattern
        import re
        if not original:
            return translated
        original_leading_spaces = len(original) - len(original.lstrip())
        translated_leading_spaces = len(translated) - len(translated.lstrip())
        original_trailing_spaces = len(original) - len(original.rstrip())
        translated_trailing_spaces = len(translated) - len(translated.rstrip())
        if translated_leading_spaces != original_leading_spaces:
            translated = translated.lstrip()
            if original_leading_spaces > 0:
                translated = ' ' * original_leading_spaces + translated
        
        if translated_trailing_spaces != original_trailing_spaces:
            translated = translated.rstrip()
            if original_trailing_spaces > 0:
                translated += ' ' * original_trailing_spaces
        original_parts = tag_pattern.split(original)
        translated_parts = tag_pattern.split(translated)
        
        if len(original_parts) != len(translated_parts):
            return translated
        result_parts = []
        for i in range(len(original_parts)):
            if original_parts[i].startswith('{') and original_parts[i].endswith('}') :
                original_tag = original_parts[i]
                translated_tag = translated_parts[i]
                translated_tag = translated_tag.strip()
                if translated_tag[0]=='{' and translated_tag[-1]=='}':
                    stripped_translated_tag = translated_tag[1:-1].strip()
                    corrected_tag =  '{'+stripped_translated_tag +'}'
                else:
                    corrected_tag=translated_parts[i]
                result_parts.append(corrected_tag)
            else:
                result_parts.append(translated_parts[i])
        return ''.join(result_parts)
    def _text_update_debug(self, *args, **kwargs):
        try:
            if not persistent.enable_translation:
                return original_update(self, *args, **kwargs)
            if hasattr(self, "text") and self.text:
                text_content = self.text[0] 
                if not isinstance(text_content, renpy.display.core.Displayable):
                    if (text_content in mdata.translation_cache)  or (text_content in mdata.retry_texts_set) or (text_content in mdata.sent_set) or (text_content in mdata.translated_set):
                        pass
                    else:
                        if  (not (text_content in PENDING_TRANSLATIONS) )and len(text_content)>1 :
                            PENDING_TRANSLATIONS.add(text_content)
                            add_text_object_to_redraw(text_content, self)
                            
        except Exception as e:
            print("Error in _text_update_debug", str(e))
        return original_update(self, *args, **kwargs)

    
    def apply_glossary(text):
        import re
        if not persistent.glossary_enabled :
            return text
        for term in sorted_glossary_terms:
            text = re.sub(r'\b' + re.escape(term) + r'\b', glossary_dic[term], text, flags=re.IGNORECASE)
        return text
    
    def hook_tssubseg(self, s):

        if (not persistent.enable_translation) or (not persistent.display_translation):
            return original_subsegment(self, s)
        if persistent.font_size_adjustment_enabled:
            if s in mdata.font_size_cache:
                self.size = mdata.font_size_cache[s]
        if isinstance(self.font, FontGroup):
            if self.font not in font_groups:
                try:
                    new_fontgroup = FontGroup() 
                    new_fontgroup.add(emoji_font, 0x1F300, 0x1FAFF)
                    new_fontgroup.add(main_font, None,None)
                    font_groups[self.font] =new_fontgroup
                    self.font = new_fontgroup
                except Exception as e:
                    print("fontgroup replace error",self.font,e)
            return original_subsegment(self, s)
        try:
            global latest_font 
            if latest_font != self.font:

                if self.font not in font_groups:
                    new_fontgroup = FontGroup() 
                    if main_font and main_font != self.font:
                        try:
                            new_fontgroup.add(main_font, None,None)
                        except Exception as e:
                            print("Failed to add main font ",main_font, e)
                            
                            font_groups[self.font] =main_font
                            self.font = main_font
                            latest_font = self.font
                            return original_subsegment(self, s)
                    try:
                        for i in range(0x00020, 0x0007f):
                            new_fontgroup.map[i]=self.font
                        print("Added current font:",self.font)
                    except Exception as e:
                        print("Failed to add current font ",self.font,e)
                    try:
                        new_fontgroup.add(emoji_font, 0x1F300, 0x1FAFF)
                    except Exception as e:
                        print("Failed to add emoji font ",fallback_font,e)
                    font_groups[self.font] =new_fontgroup
                    self.font = new_fontgroup
                    latest_font = self.font
                else:
                    self.font=font_groups[self.font]
                    latest_font = self.font
        except Exception as e:
            print("Font processing failed:", e)
            self.font = main_font
        return original_subsegment(self, s)
    

    
    
    def translate_with_llm_requests(texts, target_lang=persistent.target_language):
        global api_index
        global max_api_index
        if not persistent.enable_translation or not texts:
            return texts
        
        context_items = []
        if mdata.translation_cache:
            recent_items = list(mdata.translation_cache.items())[-persistent.appended_lines:]
            for original, translated in recent_items:
                context_items.append("Original: {}\nTranslated: {}".format(original, translated))
            previous_dialogues=get_previous_dialogue()
            if previous_dialogues:
                if (len(previous_dialogues)>=persistent.appended_lines):
                    context_items=previous_dialogues
        
        context = "\n\n".join(context_items) if context_items else "No previous translation context available"
        
        prompt = TRANSLATION_PROMPT.format(target_lang=target_lang, context=context)
        
        combined_html = text_to_comhtml(texts)
        API_KEY=persistent.api_keys[api_index]
        api_index=api_index+1
        if api_index>=max_api_index :
            api_index=0
        headers = {
            "Authorization": "Bearer {0}".format(API_KEY),
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": combined_html}
        ]
        
        data = {
            "model": persistent.model_name,
            "messages": messages,
            "temperature": persistent.temperature,
            "max_tokens": persistent.max_tokens  
        }
        
        try:
            session = session_manager.get_session()
                
            response = session.post(
                persistent.base_url,
                headers=headers,
                json=data,
                proxies=session_manager._current_proxies,
                timeout=persistent.timeout,  
            )
            
            if response.status_code == 200:
                result = response.json()
                print(result)
                translated_html = result['choices'][0]['message']['content'].strip()
                translated_texts = comhtml_to_text(translated_html,texts)
                
                return translated_texts
            else:
                print("API error: {0} - {1}".format(response.status_code, response.text))
                return texts
                
        except Exception as e:
            print("llm translation error: {0}".format(str(e)))
            return texts
    
    def translate_with_llm_urllib2(texts, target_lang=persistent.target_language):
        global api_index
        import json
        import urllib2
        max_api_index = len(persistent.api_keys)
        if not persistent.enable_translation or not texts:
            return texts
        
        context_items = []
        if mdata.translation_cache:
            recent_items = list(mdata.translation_cache.items())[-persistent.appended_lines:]
            for original, translated in recent_items:
                context_items.append("Original: {}\nTranslated: {}".format(original, translated))
            previous_dialogues=get_previous_dialogue()
            if previous_dialogues:
                if (len(previous_dialogues)>=persistent.appended_lines):
                    context_items=previous_dialogues
        
        context = "\n\n".join(context_items) if context_items else "No previous translation context available"
        prompt = TRANSLATION_PROMPT.format(target_lang=target_lang, context=context)
        
        combined_html = text_to_comhtml(texts)
        
        API_KEY = persistent.api_keys[api_index]
        api_index = (api_index + 1) % max_api_index
        
        url = persistent.base_url
        headers = {
            "Authorization": "Bearer {0}".format(API_KEY),
            "Content-Type": "application/json"
        }
        
        data = {
            "model": persistent.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": combined_html}
            ],
            "temperature": persistent.temperature,
            "max_tokens": persistent.max_tokens
        }
        
        try:
            req = urllib2.Request(url, json.dumps(data), headers)

            if persistent.proxies_enabled:
                proxy_handler = urllib2.ProxyHandler(persistent.proxies)
                opener = urllib2.build_opener(proxy_handler)
                urllib2.install_opener(opener)
            else:
                urllib2.install_opener(urllib2.build_opener())

            response = urllib2.urlopen(req, timeout=persistent.timeout)
            result = json.loads(response.read())
            
            translated_html = result['choices'][0]['message']['content'].strip()
            translated_texts = comhtml_to_text(translated_html,texts)
            
            return translated_texts
            

        except Exception as e:
            print("LLM translation error: {}".format(str(e)))
            return texts
    
    def translate_with_llm(texts, target_lang=persistent.target_language):
        if REQUESTS_AVAILABLE:
            return translate_with_llm_requests(texts, target_lang)
        else:
            return translate_with_llm_urllib2(texts, target_lang)
    
    def translate_with_freellm(texts, target_lang=persistent.target_language):
        try:
            if REQUESTS_AVAILABLE:
                return translate_with_freellm_requests(texts, target_lang)
            else:
                return translate_with_freellm_urllib2(texts, target_lang)
                return texts
        except Exception as e:
            print("translate_with_freellm error",e)
    def translate_batch(texts, target_lang=persistent.target_language,translation_service=persistent.translation_service):
        
        if (not persistent.enable_translation) or (not texts):
                print("Translation disabled or no texts provided.")
                return texts
        else:
            if translation_service == "LLM":
                return translate_with_llm(texts, target_lang)
            if translation_service == "freellm":
                return translate_with_freellm(texts, target_lang)
            if translation_service == "bing":
                combined_html,protected_contents = text_to_comhtml_edge(texts)
                if REQUESTS_AVAILABLE:
                    translated_html=_send_batch_translation_request_edge(combined_html, target_lang)
                else:
                    translated_html=_send_batch_translation_request_edge_urllib2(combined_html, target_lang)
                if translated_html==combined_html:
                    return texts
                translated_texts=comhtml_to_text_edge(translated_html,texts,protected_contents)
                return translated_texts
            try:
                combined_html = text_to_comhtml(texts)
            except Exception as e:
                print("Error in text to comhtml conversion: {0}".format(str(e)))
                return texts
            try:                
                translated_html = _send_batch_translation_request(combined_html, target_lang)
                if translated_html==combined_html:
                    return texts
                translated_texts = comhtml_to_text(translated_html,texts)
                return translated_texts
            except Exception as e:
                print("Batch translation error: {0}".format(str(e)))
                return texts
    def html_escape(s, quote=True):
        s=str(s)
        s = s.replace("&", "&amp;") 
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        if quote:
            s = s.replace('"', "&quot;")
            s = s.replace('\'', "&#x27;")
            s = s.replace("'","&#39;")
        return s   
    def html_unescape(s, quote=True):
        s=str(s)
        s = s.replace("&amp;","&") 
        s = s.replace("&lt;","<")
        s = s.replace("&gt;",">")
        if quote:
            s = s.replace("&quot;",'"')
            s = s.replace("&#x27;",'\'')
            s = s.replace("&#39;","'")
        return s         
    def text_to_comhtml(texts):
        import re
        protected_texts = [] 
        
        for text_idx, text in enumerate(texts):
            text=repr(text)
            if text.startswith("u'") or text.startswith('u"'):
                text = text[1:]
            if text[0]=="u":
                text=text[2:-1]
            else:
                text=text[1:-1] 
            def decode_escape(match):
                escape_seq = match.group(0)
                esc_char = escape_seq[1]  
                if esc_char == 'u' or esc_char == 'U':
                    hex_str = escape_seq[2:]
                    try:
                        return chr(int(hex_str, 16))
                    except:
                        return escape_seq  
                elif esc_char == 'x':
                    hex_str = escape_seq[2:]
                    try:
                        return chr(int(hex_str, 16))
                    except:
                        return escape_seq  
                elif '0' <= esc_char <= '7':
                    try:
                        return chr(int(escape_seq[1:], 8))
                    except:
                        return escape_seq
                else:
                    return escape_seq
        
            text = escaped_char_pattern.sub(decode_escape, text)
            def replace_escape(match):
                char = match.group(1)
                if char in ['\\', '"', "'", ' ', '%','&','u','U','x','X']:
                    return match.group(0)
                return '<link rel="\\{0}"/>'.format(char)
            text=html_escape(text)
            text = escape_pattern.sub(replace_escape, text)
            text = percent_pattern.sub(r'<img src="\1"/>', text)
            text = brace_pattern.sub(r'<source src="\1"/>', text)
            text = bracket_pattern.sub(r"<input type='\1'/>", text)
            text=apply_glossary(text)
            protected_texts.append(text)
        html_parts = []
        for i, text in enumerate(protected_texts):
                html_parts.append('<div id="{0}">{1}</div>'.format(i, text))
        combined_html = ''.join(html_parts)
        return combined_html
         
    def comhtml_to_text(translated_html, texts):
        import codecs
        import re
        from collections import defaultdict
        global comhtml_to_text_pattern
        try:
            translated_texts = {}
            
            id_to_contents = defaultdict(list)

            for match in comhtml_to_text_pattern.finditer(translated_html):
                
                    idx = int(match.group(1))
                    translated_text = match.group(2)
                    translated_text = img_pattern.sub(r'\1', translated_text)
                    translated_text = source_pattern.sub(r'\1', translated_text)
                    translated_text = input_pattern.sub(r'\1', translated_text)
                    try:
                        translated_text = link_pattern.sub(lambda match: codecs.decode(match.group(1), 'unicode_escape'), 
                                            translated_text)
                                            
                    except Exception as e:
                        print("Error processing match: {0}".format(str(e)))
                        print(idx, translated_text)
                        translated_text = link_pattern.sub(r'\1',translated_text)
                    translated_text = html_unescape(translated_text)
                    
                    id_to_contents[idx].append(translated_text)
                
            
            for idx, contents in id_to_contents.items():
                if idx < len(texts):
                    combined_content = ' '.join(contents) 
                    translated_texts[texts[idx]] = combined_content
                        
            return translated_texts
        except Exception as e:
            print("Error in comhtml_to_text: {0}".format(str(e)))
            print(translated_html)
            return texts
    def text_to_comhtml_edge(texts):
        import re        
        protected_texts = [] 
        protected_contents = [] 

        for text_idx, text in enumerate(texts):
            
            text = repr(text)
            if text[0] == "u":
                text = text[2:-1]
            else:
                text = text[1:-1]
            def decode_escape(match):
                escape_seq = match.group(0)
                esc_char = escape_seq[1]  
                if esc_char == 'u' or esc_char == 'U':
                    hex_str = escape_seq[2:]
                    try:
                        return chr(int(hex_str, 16))
                    except:
                        return escape_seq  
                elif esc_char == 'x':
                    hex_str = escape_seq[2:]
                    try:
                        return chr(int(hex_str, 16))
                    except:
                        return escape_seq  
                elif '0' <= esc_char <= '7':
                    try:
                        return chr(int(escape_seq[1:], 8))
                    except:
                        return escape_seq
                else:
                    return escape_seq
        
            text = escaped_char_pattern.sub(decode_escape, text)
            def add_protected_content(match):
                content = match.group(1)
                index = len(protected_contents)
                protected_contents.append(content)
                return "<b{0}>".format(index)
            def add_protected_content2(match):
                content = match.group(1)
                if content in ['\\', '"', "'", ' ', '%','&','u','U','x','X']:
                    return match.group(0)
                index = len(protected_contents)
                content="\\"+content
                protected_contents.append(content)
                return "<b{0}>".format(index)

            text=html_escape(text)
            text = escape_pattern.sub(add_protected_content2, text)
            text = percent_pattern.sub(add_protected_content, text)
            text = brace_pattern.sub(add_protected_content, text)
            text = bracket_pattern.sub(add_protected_content, text)
            text=apply_glossary(text)
            protected_texts.append(text)
        return protected_texts, protected_contents

    def comhtml_to_text_edge(translated_html, texts, protected_contents):
        import re
        from collections import defaultdict
        import codecs
        try:
            translated_texts = {}
            id_to_contents = defaultdict(list)
            
            for idx, trans_text in enumerate(translated_html):
                translated_text = trans_text
                def restore_protected_content(match):
                    index_match = re.search(r'<b(\d+)>', match.group(0))
                    if index_match:
                        index = int(index_match.group(1))
                        if index < len(protected_contents):
                            return  codecs.decode(protected_contents[index], 'unicode_escape')
                    return match.group(0)  
                translated_text = re.sub(r'<b\d+>', restore_protected_content, translated_text)
                
                translated_text = html_unescape(translated_text)                
                id_to_contents[idx].append(translated_text)
                
            for idx, contents in id_to_contents.items():
                if idx < len(texts):
                    combined_content = ' '.join(contents) 
                    translated_texts[texts[idx]] = combined_content
                    
            return translated_texts
            
        except Exception as e:
            print("Error in comhtml_to_text: {0}".format(str(e)))
            print(translated_html)
            return texts
    

    def quit_save_translation_cache():
        import json
        if persistent.enable_translation and len(mdata.translation_cache)>persistent.last_saved_cache_size:
            try:
                with open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(mdata.translation_cache, f, ensure_ascii=False, indent=2)
                print("translation cache saved")
            except:
                import codecs
                with codecs.open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(mdata.translation_cache, f, ensure_ascii=False, indent=2)
            
    
    def hook_segment_trans(self, tokens, style, renders, text_displayable):
        try:
            if not persistent.enable_translation  :
                return original_cts(self, tokens, style, renders, text_displayable)

            if hasattr(text_displayable, "text") and text_displayable.text:
                text_content =text_displayable.text[0]
                if not  isinstance(text_content, renpy.display.core.Displayable):

                    if (text_content in mdata.translation_cache) or (text_content in mdata.retry_texts_set) or (text_content in mdata.sent_set):
                        pass
                    else:
                        if  (not (text_content  in PENDING_TRANSLATIONS) )and len(text_content)>1 : 
                            PENDING_TRANSLATIONS.add(text_content)
                            add_text_object_to_redraw(text_content, text_displayable)      
                else:
                    return original_cts(self, tokens, style, renders, text_displayable)
            if not persistent.display_translation or len(text_content)<3 :
                return original_cts(self, tokens, style, renders, text_displayable)
            if text_content in mdata.translation_cache:
                try:
                    new_tokens=text_displayable.tokenize([mdata.translation_cache[text_content]])
                except Exception as e:
                    print("Error in tokenize", str(e))
                    add_text_object_to_redraw(text_content, text_displayable) 
                    return original_cts(self, tokens, style, renders, text_displayable)
                try:
                    new_tokens= text_displayable.apply_custom_tags(new_tokens)
                except Exception as e:
                    print("Error in apply_custom_tags", str(e))
                    pass
                try:
                    new_tokens = new_get_displayables(text_displayable,new_tokens)
                except Exception as e:
                    print("Error in new_get_displayables", str(e))
                    pass
                try:
                    result_tokens = []
                    text_token_index = 0
                    new_text_tokens = [token for token in new_tokens if token[0] == 1]
                    old_text_tokens = [token for token in tokens if token[0] == 1]
                    if len(new_text_tokens)!=len(old_text_tokens):
                        try:
                            if persistent.show_comparison:
                                new_tokens.append((3," "))
                                new_tokens=new_tokens+tokens
                            return original_cts(self, new_tokens, style, renders, text_displayable)
                        except:
                            print("Token repalce wrong",new_tokens)
                            pass
                    new_text_token_index = 0
                    for token in tokens:
                        typi, text = token
                        if typi == 1: 
                            if new_text_token_index >= len(new_text_tokens): 
                                result_tokens.append(token)
                                continue
                            if text==' ' and  new_text_tokens[new_text_token_index][1]!=' ':

                                result_tokens.append(token)
                                text_token_index += 1
                                continue
                            if new_text_token_index < len(new_text_tokens):
                                result_tokens.append(new_text_tokens[new_text_token_index])
                                new_text_token_index += 1
                                text_token_index += 1
                                    
                        else:
                            result_tokens.append(token)
                    if len(result_tokens) < len(new_tokens):
                        remaining_tokens = new_tokens[len(result_tokens) - len(new_tokens):]  
                        for token in remaining_tokens:
                            result_tokens.append(token)
                            print("appending extra new tokens", token)
                    if persistent.show_comparison:
                                result_tokens.append((3," "))
                                result_tokens=result_tokens+tokens
                    return original_cts(self, result_tokens, style, renders, text_displayable)
                except Exception as e:
                    print("Error in token replacement", str(e))
                    print("new_tokens:", new_tokens)
                    print("original tokens:", tokens)
            else:
                PENDING_TRANSLATIONS.add(text_content)
                add_text_object_to_redraw(text_content, text_displayable)

        except Exception as e:
            print("Error in hook_segment", str(e))
        return original_cts(self, tokens, style, renders, text_displayable)
    
    def tts_trans(self):
        if not (persistent.enable_translation and persistent.display_translation):
            return original_tts(self)
        trans_texts=[]
        for i in self.text:
            
            if i in mdata.translation_cache:
                if isinstance(i,str) or isinstance(i,basestring):
                    if i == r"Self-voicing enabled. Press 'v' to disable.":
                        return original_tts(self)
                trans_texts.append(mdata.translation_cache[i])
            else:
                trans_texts.append(i)
        Text_tmp=Text(trans_texts, self.style)
        return original_tts(Text_tmp)
    
    def new_get_displayables(text_displayable, tokens):
        try:
            displayables = text_displayable.displayables
            new_tokens = []
            for t in tokens:
                kind, text = t
                if kind == 4:
                    new_tokens.append(t)
                    continue
                if kind == 2:
                    tag, _, value = text.partition("=")
                    if tag == "image" and value:
                        d = renpy.easy.displayable(value)
                        displayables.add(d)
                        new_tokens.append((4, d))
                        continue

                new_tokens.append(t)
        except Exception as e:
            print("Error in new_get_displayables", str(e))
            return tokens
        return new_tokens

    
    class SessionManager:
        def __init__(self):
            self._session = None
            self._session_urllib2 = None
            self._last_proxy_change = 0
            self._current_proxies = None
            
        def get_session(self):
            import functools
            if REQUESTS_AVAILABLE:
                import requests
                if self._session is None:
                    self._session = requests.Session()
                    adapter = requests.adapters.HTTPAdapter(
                        pool_connections=10,
                        pool_maxsize=100,
                        max_retries=3,  
                        pool_block=False
                    )
                    self._session.mount('http://', adapter)
                    self._session.mount('https://', adapter)
                    self._session.request = functools.partial(
                        self._session.request, 
                        timeout=(3.05, 30) 
                    )
                return self._session
            return None
            
                    
        def update_proxies(self):
            current_proxies = get_proxies()
            if current_proxies != self._current_proxies:
                if self._session:
                    self._session.proxies.update(current_proxies or {})
                self._current_proxies = current_proxies
                self._last_proxy_change = renpy.time.time()
                
        def close(self):
            if self._session:
                self._session.close()
                self._session = None
            self._session_urllib2 = None
    
    

    def cleanup_sessions():
        session_manager.close()

    
    def toggle_translation():
        try:
            persistent.display_translation = not persistent.display_translation
            renpy.save_persistent()
            mdata.translation_cache = {}
            if persistent.display_translation:
                load_translation_cache()
            else:
                save_translation_cache()
            renpy.call_in_new_context("_force_redraw")
            renpy.restart_interaction()
            renpy.hide_screen("pep_hidden_marker")
            renpy.show_screen("pep_hidden_marker")
            return
        except:
            return
    def process_variable_texts():
        global var_texts_dict, var_pattern
        if not var_texts_dict:
            return False
        
        all_texts_to_process = set()
        for text_list in var_texts_dict.values():
            all_texts_to_process.update(text_list)
        
        processed_texts = set()
        
        for text in all_texts_to_process:
            variables_in_text = var_pattern.findall(text)
            all_vars_defined = True
            var_values = {}
            
            for var_name in variables_in_text:
                try:
                    var_value = eval(var_name)
                    if var_value is not None:
                        var_values[var_name] = str(var_value)
                    else:
                        all_vars_defined = False
                        break
                except Exception as e :
                    all_vars_defined = False
                    continue
            if all_vars_defined and var_values:
                replaced_text = text
                for var_name, var_value in var_values.items():
                    replaced_text = replaced_text.replace("[{0}]".format(var_name), var_value)
                if text in mdata.translation_cache:
                    original_translation = mdata.translation_cache[text]
                    replaced_translation = original_translation
                    for var_name, var_value in var_values.items():
                        replaced_translation = replaced_translation.replace("[{0}]".format(var_name), var_value)
                    mdata.translation_cache[replaced_text] = replaced_translation
                    mdata.translated_set.add(replaced_translation)
                processed_texts.add(text)
        for var_name, text_list in list(var_texts_dict.items()):
            remaining_texts = [text for text in text_list if text not in processed_texts]
            
            if remaining_texts:
                var_texts_dict[var_name] = remaining_texts
            else:
                del var_texts_dict[var_name]
        return len(var_texts_dict) > 0
    
    trans_init()
    if REQUESTS_AVAILABLE:
        session_manager = SessionManager()
        session_manager.update_proxies()
    class ModDataContainer(object):
        pass
    mdata = ModDataContainer()
    DIC_CONSTANTS = ["translation_cache","font_size_cache","TEXT_OBJECTS_TO_REDRAW"]
    for var_name in DIC_CONSTANTS:
        val = {}
        setattr(mdata, var_name, val)
    SET_CONSTANTS=["retry_texts_set", "sent_set", "sent_set_twice","PRESCAN_TEXTS","translated_set","prescan_texts"]
    for var_name in SET_CONSTANTS:
        val = set()
        setattr(mdata, var_name, val)


    original_update = renpy.text.text.Text.update
    renpy.text.text.Text.update = _text_update_debug  

    original_subsegment = renpy.text.text.TextSegment.subsegment  
    renpy.text.text.TextSegment.subsegment = hook_tssubseg

    config.periodic_callbacks.append(process_pending_translations)
    config.periodic_callbacks.append(process_redrawing_translations)
    try:
        config.quit_callbacks.append(quit_save_translation_cache)
        if REQUESTS_AVAILABLE:
            config.quit_callbacks.append(cleanup_sessions)
    except:
        print("config.quit_callbacks.append error")
        pass
    original_cts=renpy.text.text.Layout.segment
    renpy.text.text.Layout.segment=hook_segment_trans
    if persistent.enable_rtl:
        renpy.config.rtl=True
    original_tts=renpy.text.text.Text._tts
    renpy.text.text.Text._tts=tts_trans
    
    if "pep_hidden_marker" not in config.overlay_screens:
        config.overlay_screens.append("pep_hidden_marker")   
init 999 python:
    _original_say_menu_text_filter = config.say_menu_text_filter

    def translation_chain_filter(text):
        current_text = text
        if _original_say_menu_text_filter is not None:
            try:
                current_text = _original_say_menu_text_filter(text)
            except Exception as e:
                print("Original filter error: {}".format(e))
        if (not persistent.enable_translation) or (persistent.PRESCAN_FLAG==0):
            return current_text
        if current_text in mdata.translation_cache:
            return current_text
        if (current_text not in mdata.retry_texts_set) and( current_text not in mdata.sent_set) and ( current_text not in mdata.PRESCAN_TEXTS) and (current_text not in mdata.translated_set):
            PENDING_TRANSLATIONS.add(current_text)            
        return current_text

    config.say_menu_text_filter = translation_chain_filter
screen force_redraw():
    timer .1 action Return()
label _force_redraw:
    call screen force_redraw
    pause .1
    return
screen pep_hidden_marker():
        zorder 999 
        
        button:
            xalign persistent.x_button_pos
            yalign persistent.y_button_pos
            xpadding 5
            ypadding 5
            text "<<<" :
                if persistent.display_translation:
                    color "#9a9af8"
                else:
                    color "#f7a0a3ff"  
            action Function(toggle_translation)
