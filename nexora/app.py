import flet as ft

from .i18n import TEXT
from .auth import AuthService
from .storage import LocalStore


NAV_ITEMS = [
    "home", "assistant", "files", "notes", "community",
    "messages", "tasks", "learning", "search", "settings",
]


def main(page: ft.Page):
    page.title = "NEXORA — Smart Digital World"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B1020"
    page.padding = 0

    state = {"lang": "ar", "dark": True, "user": None}
    auth = AuthService()
    store = LocalStore()
    accent = "#7C5CFC"

    def t(key):
        return TEXT[state["lang"]].get(key, key)

    def notify(message):
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def metric_card(label, value, symbol):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(symbol, size=28),
                    ft.Column(
                        [
                            ft.Text(
                                value,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color="white",
                            ),
                            ft.Text(label, color="#AAB4D0"),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
            padding=16,
            bgcolor="#151D35",
            border_radius=16,
        )

    def section_content(section):
        descriptions = {
            "home": "home_desc",
            "assistant": "assistant_desc",
            "files": "files_desc",
            "notes": "notes_desc",
            "community": "community_desc",
            "messages": "messages_desc",
            "tasks": "tasks_desc",
            "learning": "learning_desc",
            "search": "search_desc",
            "settings": "settings_desc",
        }

        controls = [
            ft.Text(
                t(section),
                size=27,
                weight=ft.FontWeight.BOLD,
                color="white" if state["dark"] else "#18213A",
            ),
            ft.Text(t(descriptions[section]), color="#AAB4D0"),
        ]

        if section == "home":
            controls.extend(
                [
                    metric_card(
                        t("quick_notes"),
                        str(len(store.get_items("notes"))),
                        "📝",
                    ),
                    metric_card(
                        t("my_tasks"),
                        str(len(store.get_items("tasks"))),
                        "✅",
                    ),
                    metric_card(t("community"), "—", "👥"),
                    ft.Text(
                        t("modules"),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="white" if state["dark"] else "#18213A",
                    ),
                    ft.Text(t("modules_desc"), color="#AAB4D0"),
                ]
            )

        elif section == "notes":
            note_input = ft.TextField(
                label=t("write_note"),
                multiline=True,
                min_lines=2,
                max_lines=5,
            )

            def save_note(e):
                value = (note_input.value or "").strip()
                if value:
                    store.add_item("notes", value)
                    notify(t("saved_local"))
                    render("notes")

            controls.extend(
                [
                    note_input,
                    ft.ElevatedButton(t("save"), on_click=save_note),
                    ft.Column(
                        [
                            ft.ListTile(title=ft.Text(item))
                            for item in store.get_items("notes")[-20:][::-1]
                        ],
                        spacing=4,
                    ),
                ]
            )

        elif section == "tasks":
            task_input = ft.TextField(label=t("new_task"))

            def add_task(e):
                value = (task_input.value or "").strip()
                if value:
                    store.add_item("tasks", value)
                    notify(t("saved_local"))
                    render("tasks")

            controls.extend(
                [
                    ft.Row(
                        [
                            ft.Container(content=task_input, expand=True),
                            ft.IconButton(
                                icon=ft.icons.ADD_CIRCLE,
                                tooltip=t("save"),
                                on_click=add_task,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Text("☐"),
                                title=ft.Text(item),
                            )
                            for item in store.get_items("tasks")[-30:][::-1]
                        ],
                        spacing=2,
                    ),
                ]
            )

        elif section == "settings":
            controls.extend(
                [
                    ft.Text(t("language"), color="#AAB4D0"),
                    ft.ElevatedButton(
                        "العربية" if state["lang"] == "en" else "English",
                        on_click=lambda e: toggle_lang(),
                    ),
                    ft.Switch(
                        label=t("dark_mode"),
                        value=state["dark"],
                        on_change=change_theme,
                    ),
                    ft.Text(t("account_info"), color="#AAB4D0"),
                    ft.Text(t("auth_note"), color="#AAB4D0", size=12),
                ]
            )

        elif section == "messages":
            controls.append(ft.Text(t("messages_safety"), color="#F5C66A"))

        elif section == "community":
            controls.append(ft.Text(t("community_safety"), color="#F5C66A"))

        else:
            controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("🚧", size=42),
                            ft.Text(t("module_coming"), color="white"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=24,
                    alignment=ft.alignment.center,
                    bgcolor="#151D35",
                    border_radius=18,
                )
            )

        return ft.Column(
            controls,
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def toggle_lang():
        state["lang"] = "en" if state["lang"] == "ar" else "ar"
        render("home")

    def change_theme(e):
        state["dark"] = bool(e.control.value)
        render("settings")

    def close_dialog():
        if page.dialog:
            page.dialog.open = False
            page.update()

    def show_auth():
        email = ft.TextField(
            label=t("email"),
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        password = ft.TextField(
            label=t("password"),
            password=True,
            can_reveal_password=True,
        )

        def email_login(e):
            try:
                result = auth.sign_in(email.value, password.value)
                state["user"] = result
                notify(t("login_ok"))
                close_dialog()
            except Exception as exc:
                notify(f"{t('auth_error')}: {exc}")

        def google_login(e):
            try:
                url = auth.google_sign_in()
                page.launch_url(url)
            except Exception as exc:
                notify(f"{t('auth_error')}: {exc}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(t("account")),
            content=ft.Column([email, password], tight=True, width=300),
            actions=[
                ft.TextButton(t("login"), on_click=email_login),
                ft.TextButton(t("google"), on_click=google_login),
                ft.TextButton(t("close"), on_click=lambda e: close_dialog()),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def render(section="home"):
        if section not in NAV_ITEMS:
            section = "home"

        try:
            page.clean()
            page.bgcolor = "#0B1020" if state["dark"] else "#F3F5FB"

            header = ft.Container(
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    width=8,
                                    height=34,
                                    bgcolor=accent,
                                    border_radius=6,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            "NEXORA",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color="white",
                                        ),
                                        ft.Text(
                                            "SMART DIGITAL WORLD",
                                            size=9,
                                            color="#AAB4D0",
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Row(
                            [
                                ft.TextButton(
                                    "🌐",
                                    tooltip=t("language"),
                                    on_click=lambda e: toggle_lang(),
                                ),
                                ft.TextButton(
                                    "👤",
                                    tooltip=t("account"),
                                    on_click=lambda e: show_auth(),
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(left=16, right=12, top=12, bottom=8),
            )

            nav = ft.Container(
                content=ft.Row(
                    [
                        ft.TextButton(
                            t(item),
                            on_click=lambda e, selected=item: render(selected),
                        )
                        for item in NAV_ITEMS
                    ],
                    spacing=2,
                    scroll=ft.ScrollMode.AUTO,
                ),
                bgcolor="#10182D",
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            )

            content = ft.Container(
                content=section_content(section),
                padding=16,
                expand=True,
            )

            page.add(
                ft.Column(
                    [
                        header,
                        ft.Divider(height=1, color="#26314D"),
                        nav,
                        content,
                    ],
                    spacing=0,
                    expand=True,
                )
            )
            page.update()

        except Exception as exc:
            # A visible diagnostic screen is more useful than a silent black page.
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("NEXORA", size=26, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                "حدث خطأ أثناء تشغيل الشاشة."
                                if state["lang"] == "ar"
                                else "The screen could not be displayed.",
                                size=17,
                            ),
                            ft.Text(
                                f"{type(exc).__name__}: {exc}",
                                size=12,
                                color="#F5C66A",
                            ),
                            ft.ElevatedButton(
                                "إعادة المحاولة" if state["lang"] == "ar" else "Retry",
                                on_click=lambda e: render("home"),
                            ),
                        ],
                        spacing=16,
                    ),
                    padding=24,
                    expand=True,
                    alignment=ft.alignment.center,
                )
            )
            page.update()

    render()
