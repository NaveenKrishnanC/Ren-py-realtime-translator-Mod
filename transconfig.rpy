
init -999 python:
    import importlib
    import inspect
    if not hasattr(renpy.store, 'my_old_show_screen'):
        renpy.store.my_old_show_screen = renpy.show_screen
    def my_show_screen(_screen_name, *_args, **kwargs):
        if _screen_name == 'preferences':
            _screen_name = 'my_preferences'
        return renpy.store.my_old_show_screen(_screen_name, *_args, **kwargs)
    
    renpy.show_screen = my_show_screen
    def save_persistent():
        renpy.save_persistent()

screen my_preferences():
    tag menu
    use preferences
    vbox:
        align(0.99, 0.99)
        textbutton _("Translation Settings") action Show("translation_settings")
screen translation_settings():
    tag menu
    
    vbox:
        style_prefix "preferences"
        xfill True
        yfill True
        
        vbox:
            xalign 0.5
            yalign 0.5
            spacing gui.pref_spacing
            
            label _("Translation Settings"):
                style "game_menu_label"
                xalign 0.5
            
            viewport:
                id "translation_viewport"
                scrollbars "vertical"
                mousewheel True
                draggable True
                xmaximum int(config.screen_width * 0.8)
                ymaximum int(config.screen_height * 0.7)
                
                vbox:
                    spacing gui.pref_spacing
                    
                    hbox:
                        box_wrap True
                        spacing gui.pref_spacing
                        vbox:
                            style_prefix "pref"
                            label _("Enable Translation")
                            textbutton str(persistent.enable_translation) action Function(update_cache)
                        
                        vbox:
                            style_prefix "pref"
                            label _("Target Language")
                            textbutton str(persistent.target_language) or _("Select") action Function(renpy.call_in_new_context, "change_target_language")
                    
                    hbox:
                        box_wrap True
                        spacing gui.pref_spacing
                        vbox:
                            style_prefix "pref"
                            label _("Translation Service")
                            hbox:
                                spacing 5
                                textbutton "Google" action [SetField(persistent, "translation_service", "google"), Function(save_persistent)]
                                textbutton "LLM" action [SetField(persistent, "translation_service", "LLM"), Function(save_persistent)]
                                textbutton "bing" action [SetField(persistent, "translation_service", "bing"), Function(save_persistent)]
                                textbutton "freellm" action [SetField(persistent, "translation_service", "freellm"), Function(save_persistent)]
                        vbox:
                                label _("Show Comparison Enabled")
                                textbutton _("Toggle") action ToggleField(persistent, "show_comparison")
                    if persistent.translation_service == "LLM":
                        vbox:
                            style_prefix "pref"
                            spacing gui.pref_spacing
                            label _("LLM Settings")
                           
                            hbox:
                                box_wrap True
                                spacing gui.pref_spacing
                                vbox:
                                    label _("Max Tokens")
                                    textbutton str(persistent.max_tokens) action Function(renpy.call_in_new_context, "change_max_tokens")
                            
                                vbox:
                                    label _("Temperature")
                                    textbutton str(persistent.temperature) action Function(renpy.call_in_new_context, "change_temperature")
                            
                                vbox:
                                    label _("Timeout")
                                    textbutton str(persistent.timeout) action Function(renpy.call_in_new_context, "change_timeout")

                    vbox:
                        style_prefix "pref"
                        spacing gui.pref_spacing
                        label _("Advanced Settings")
                        
                        hbox:
                            box_wrap True
                            spacing gui.pref_spacing
                            vbox:
                                label _("Appended Lines (context)")
                                textbutton str(persistent.appended_lines) action Function(renpy.call_in_new_context, "change_appended_lines")
                            
                            vbox:
                                label _("Proxies Enabled")
                                textbutton _("Toggle") action ToggleField(persistent, "proxies_enabled")

                        
                        hbox:
                            box_wrap True
                            spacing gui.pref_spacing
                            vbox:
                                label _("Font Size Adjustment Enabled")
                                textbutton _("Toggle") action ToggleField(persistent, "font_size_adjustment_enabled")
                            vbox:
                                label _("Min Scale")
                                textbutton str(persistent.font_size_adjustment_min_scale) action Function(renpy.call_in_new_context, "change_min_scale")
                        
                            vbox:
                                label _("Max Scale")
                                textbutton str(persistent.font_size_adjustment_max_scale) action Function(renpy.call_in_new_context, "change_max_scale")
                        
                            vbox:
                                label _("Length Threshold")
                                textbutton str(persistent.font_size_adjustment_length_threshold) action Function(renpy.call_in_new_context, "change_length_threshold")
                        
                        hbox:
                            box_wrap True
                            spacing gui.pref_spacing
                            vbox:
                                label _("Time Interval")
                                textbutton str(persistent.time_interval) action Function(renpy.call_in_new_context, "change_time_interval")
                            
                            vbox:
                                label _("Translation Font")
                                textbutton persistent.trans_font or _("Default") action Function(renpy.call_in_new_context, "change_trans_font")
                            
                            vbox:
                                label _("Enable RTL (Right-to-Left)")
                                textbutton _("Toggle") action ToggleField(persistent, "enable_rtl")
            
            hbox:
                xalign 0.5
                textbutton _("Back") action [Function(save_persistent), Return()]:
                    style "navigation_button"
                    xminimum int(config.screen_width * 0.15)
init python:
    def update_cache():
        global translation_cache
        persistent.enable_translation = not persistent.enable_translation
        persistent.display_translation = persistent.enable_translation
        translation_cache = {}
        if persistent.enable_translation:
            load_translation_cache()
        else:            
            save_translation_cache()
        save_persistent()
        return
    

label change_target_language:
    $ new_value = renpy.input(_("Enter target language code:"), default=persistent.target_language, length=5)
    $ persistent.target_language = new_value.strip() if new_value.strip() else persistent.target_language
    $ save_persistent()
    return

label change_max_tokens:
    $ new_value = renpy.input(_("Enter max tokens:"), default=str(persistent.max_tokens), length=10)
    if new_value.strip() and new_value.strip().isdigit():
        $ persistent.max_tokens = int(new_value)
        $ save_persistent()
    return

label change_temperature:
    $ new_value = renpy.input(_("Enter temperature:"), default=str(persistent.temperature), length=10)
    if new_value.strip():
        python:
            try:
                persistent.temperature = float(new_value)
                save_persistent()
            except:
                pass  
    return

label change_timeout:
    $ new_value = renpy.input(_("Enter timeout:"), default=str(persistent.timeout), length=10)
    if new_value.strip():
        python:
            try:
                persistent.timeout = float(new_value)
                save_persistent()
            except:
                pass  
    return

label change_appended_lines:
    $ new_value = renpy.input(_("Enter appended lines:"), default=str(persistent.appended_lines), length=5)
    if new_value.strip() and new_value.strip().isdigit():
        $ persistent.appended_lines = int(new_value)
        $ save_persistent()
    return

label change_proxies:
    $ current_value = json.dumps(persistent.proxies)
    $ new_value = renpy.input(_("Enter proxies (JSON format):"), default=current_value, length=100)
    if new_value.strip():
        python:
            try:
                persistent.proxies = json.loads(new_value)
                save_persistent()
            except:
                pass  
    return

label change_min_scale:
    $ new_value = renpy.input(_("Enter min scale:"), default=str(persistent.font_size_adjustment_min_scale), length=5)
    if new_value.strip():
        python:
            try:
                persistent.font_size_adjustment_min_scale = float(new_value)
                save_persistent()
            except:
                pass  
    return

label change_max_scale:
    $ new_value = renpy.input(_("Enter max scale:"), default=str(persistent.font_size_adjustment_max_scale), length=5)
    if new_value.strip():
        python:
            try:
                persistent.font_size_adjustment_max_scale = float(new_value)
                save_persistent()
            except:
                pass  
    return

label change_length_threshold:
    $ new_value = renpy.input(_("Enter length threshold:"), default=str(persistent.font_size_adjustment_length_threshold), length=5)
    if new_value.strip() and new_value.strip().isdigit():
        $ persistent.font_size_adjustment_length_threshold = float(new_value)
        $ save_persistent()
    return

label change_time_interval:
    $ new_value = renpy.input(_("Enter time interval:"), default=str(persistent.time_interval), length=5)
    if new_value.strip():
        python:
            try:
                persistent.time_interval = float(new_value)
                save_persistent()
            except:
                pass  
    return

label change_trans_font:
    $ new_value = renpy.input(_("Enter translation font:"), default=persistent.trans_font, length=50)
    $ persistent.trans_font = new_value.strip() if new_value.strip() else persistent.trans_font
    $ save_persistent()
    return
