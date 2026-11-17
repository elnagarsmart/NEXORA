import flet as ft
from .i18n import TEXT
from .auth import AuthService
from .storage import LocalStore

def main(page: ft.Page):
    page.title = "NEXORA — Smart Digital World"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B1020"
    page.padding = 0
    page.window_min_width = 360
    page.window_min_height = 640

    state = {"lang": "ar", "dark": True, "user": None}
    auth = AuthService()
    store = LocalStore()
    accent = "#7C5CFC"
    nav_items = [
        ("home", "home", "home"), ("assistant", "auto_awesome", "assistant"),
        ("files", "folder_open", "files"), ("notes", "edit_note", "notes"),
        ("community", "groups", "community"), ("messages", "chat_bubble_outline", "messages"),
        ("tasks", "task_alt", "tasks"), ("learning", "school", "learning"),
        ("search", "search", "search"), ("settings", "settings", "settings"),
    ]

    def t(key):
        return TEXT[state["lang"]].get(key, key)

    def notify(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def section_content(section):
        title = t(section)
        descriptions = {
            "home": "home_desc", "assistant": "assistant_desc", "files": "files_desc",
            "notes": "notes_desc", "community": "community_desc", "messages": "messages_desc",
            "tasks": "tasks_desc", "learning": "learning_desc", "search": "search_desc",
            "settings": "settings_desc"
        }
        controls = [ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(t(descriptions.get(section, "coming_soon")), color="#AAB4D0")]
        if section == "home":
            controls += [
                ft.ResponsiveRow([
                    metric_card(t("quick_notes"), str(len(store.get_items("notes"))), "edit_note"),
                    metric_card(t("my_tasks"), str(len(store.get_items("tasks"))), "task_alt"),
                    metric_card(t("community"), "—", "groups"),
                ], spacing=12, run_spacing=12),
                ft.Text(t("modules"), size=18, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(t("modules_desc"), color="#AAB4D0")
            ]
        elif section == "notes":
            note_input = ft.TextField(label=t("write_note"), multiline=True, min_lines=2, max_lines=4, expand=True)
            def save_note(e):
                if note_input.value and note_input.value.strip():
                    store.add_item("notes", note_input.value.strip())
                    note_input.value = ""
                    notify(t("saved_local"))
                    render("notes")
            controls += [note_input, ft.ElevatedButton(t("save"), icon="save", on_click=save_note),
                         ft.Column([ft.ListTile(title=ft.Text(x)) for x in store.get_items("notes")[-10:]])]
        elif section == "tasks":
            task_input = ft.TextField(label=t("new_task"), expand=True)
            def add_task(e):
                if task_input.value and task_input.value.strip():
                    store.add_item("tasks", task_input.value.strip())
                    notify(t("saved_local"))
                    render("tasks")
            controls += [ft.Row([task_input, ft.IconButton("add_circle", on_click=add_task)]),
                         ft.Column([ft.ListTile(leading=ft.Icon("radio_button_unchecked"), title=ft.Text(x))
                                    for x in store.get_items("tasks")[-15:]])]
        elif section == "settings":
            controls += [
                ft.Text(t("language"), color="white"),
                ft.SegmentedButton(selected={state["lang"]}, on_change=change_lang,
                    segments=[ft.Segment(value="ar", label=ft.Text("العربية")),
                              ft.Segment(value="en", label=ft.Text("English"))]),
                ft.Switch(label=t("dark_mode"), value=state["dark"], on_change=change_theme),
                ft.Text(t("account_info"), color="#AAB4D0"),
                ft.Text(t("auth_note"), color="#AAB4D0", size=12)
            ]
        elif section == "messages":
            controls.append(ft.Text(t("messages_safety"), color="#F5C66A"))
        elif section == "community":
            controls.append(ft.Text(t("community_safety"), color="#F5C66A"))
        else:
            controls.append(ft.Container(
                content=ft.Column([ft.Icon("construction", size=42, color=accent),
                                   ft.Text(t("module_coming"), color="white")],
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30, alignment=ft.alignment.center,
                bgcolor="#151D35", border_radius=18))
        return ft.Column(controls, spacing=18, scroll=ft.ScrollMode.AUTO, expand=True)

    def metric_card(label, value, icon):
        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            content=ft.Row([ft.Icon(icon, color="#B9A9FF", size=26),
                            ft.Column([ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color="white"),
                                       ft.Text(label, color="#AAB4D0")], spacing=2)]),
            padding=18, bgcolor="#151D35", border_radius=16)

    def render(section="home"):
        page.clean()
        page.bgcolor = "#0B1020" if state["dark"] else "#F3F5FB"
        header = ft.Row([
            ft.Row([ft.Container(width=9, height=30, bgcolor=accent, border_radius=6),
                    ft.Column([ft.Text("NEXORA", size=20, weight=ft.FontWeight.BOLD, color="white"),
                               ft.Text("SMART DIGITAL WORLD", size=9, color="#AAB4D0")], spacing=0)]),
            ft.Row([ft.IconButton("translate", tooltip=t("language"), on_click=lambda e: toggle_lang()),
                    ft.IconButton("account_circle", tooltip=t("account"), on_click=lambda e: show_auth())])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        sidebar = ft.NavigationRail(
            selected_index=[x[0] for x in nav_items].index(section),
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=76, min_extended_width=180,
            destinations=[ft.NavigationRailDestination(icon=icon, label=t(key))
                          for key, icon, _ in nav_items],
            on_change=lambda e: render(nav_items[e.control.selected_index][0]),
            bgcolor="#10182D"
        )
        body = ft.Column([header, ft.Divider(color="#26314D"), section_content(section)],
                         expand=True, spacing=18)
        page.add(ft.Row([sidebar, ft.VerticalDivider(width=1, color="#26314D"),
                         ft.Container(content=body, expand=True, padding=16)],
                        expand=True, spacing=0))
        page.update()

    def change_lang(e):
        state["lang"] = e.control.selected.pop() if e.control.selected else "ar"
        render("settings")

    def toggle_lang():
        state["lang"] = "en" if state["lang"] == "ar" else "ar"
        render("home")

    def change_theme(e):
        state["dark"] = e.control.value
        render("settings")

    def show_auth():
        email = ft.TextField(label=t("email"), keyboard_type=ft.KeyboardType.EMAIL)
        password = ft.TextField(label=t("password"), password=True, can_reveal_password=True)
        def email_login(e):
            try:
                result = auth.sign_in(email.value, password.value)
                state["user"] = result
                notify(t("login_ok"))
            except Exception as ex:
                notify(f"{t('auth_error')}: {ex}")
        def google_login(e):
            try:
                url = auth.google_sign_in()
                page.launch_url(url)
            except Exception as ex:
                notify(f"{t('auth_error')}: {ex}")
        dlg = ft.AlertDialog(
            modal=True, title=ft.Text(t("account")),
            content=ft.Column([email, password], tight=True, width=320),
            actions=[ft.TextButton(t("login"), on_click=email_login),
                     ft.TextButton(t("google"), on_click=google_login),
                     ft.TextButton(t("close"), on_click=lambda e: close_dialog())])
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    render()
