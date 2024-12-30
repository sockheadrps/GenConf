APP_CSS = """
    #title {
        padding: 1;
    }
    
    #instructions {
        padding: 1;
    }
    
    #select_label, #pre_run_label, #post_run_label, #entries_label {
        padding: 1;
    }
    
    Input {
        margin: 1;
        width: 100%;
    }
    
    Select {
        margin: 1;
        width: 100%;
    }
    
    Button {
        margin: 1;
        width: 100%;
    }
    
    ListView {
        height: 10;
        border: solid green;
        margin: 1;
    }

    #run_container {
        layout: horizontal;
        height: auto;
    }

    #pre_run_container, #post_run_container {
        width: 50%;
        height: auto;
        padding: 1;
    }

    #db_controls {
        layout: vertical;
        height: auto;
        margin: 1;
    }

    /* Hide all tab content by default */
    #equipment_check_content,
    #database_content,
    #report_content {
        display: none;
    }

    /* Show active tab content */
    #equipment_check_content.show,
    #database_content.show,
    #report_content.show {
        display: block;
    }

    #db_entries_container {
        layout: horizontal;
        height: auto;
    }

    #pre_entries_container, #post_entries_container {
        width: 50%;
        height: auto;
        padding: 1;
    }

    #db_button_container {
        layout: horizontal;
        height: auto;
        margin: 1;
    }

    #db_button_container Button {
        width: 50%;
    }
"""
