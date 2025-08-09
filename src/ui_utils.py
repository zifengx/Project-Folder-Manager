"""
Common UI utilities and dialog helpers
"""
import tkinter as tk
from tkinter import messagebox
import datetime
from typing import Optional


class DialogManager:
    """Manages common dialog operations"""
    
    @staticmethod
    def center_dialog(dialog: tk.Toplevel, parent: tk.Widget):
        """Center dialog on parent window"""
        dialog.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        dialog_w = dialog.winfo_width()
        dialog_h = dialog.winfo_height()
        x = parent_x + (parent_w // 2) - (dialog_w // 2)
        y = parent_y + (parent_h // 2) - (dialog_h // 2)
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def create_modal_dialog(parent: tk.Widget, title: str, width: int = None, height: int = None) -> tk.Toplevel:
        """Create a modal dialog with standard settings"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.grab_set()
        
        # If width/height provided, set fixed size, otherwise auto-size
        if width and height:
            dialog.geometry(f"{width}x{height}")
        
        return dialog
    
    @staticmethod
    def auto_size_and_center(dialog: tk.Toplevel, parent: tk.Widget):
        """Auto-size dialog to fit content and center it"""
        dialog.update_idletasks()
        
        # Get required size
        req_width = dialog.winfo_reqwidth()
        req_height = dialog.winfo_reqheight()
        
        # Add some padding
        width = req_width + 40
        height = req_height + 20
        
        # Set size and center
        dialog.geometry(f"{width}x{height}")
        DialogManager.center_dialog(dialog, parent)
    
    @staticmethod
    def confirm_dialog(parent: tk.Widget, title: str, message: str) -> bool:
        """Show confirmation dialog"""
        dialog = DialogManager.create_modal_dialog(parent, title)
        
        tk.Label(dialog, text=message, wraplength=300).pack(padx=15, pady=12)
        
        result = {"confirmed": False}
        
        def on_yes():
            result["confirmed"] = True
            dialog.destroy()
        
        def on_no():
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        tk.Button(btn_frame, text="Yes", command=on_yes, width=10).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="No", command=on_no, width=10).pack(side=tk.LEFT, padx=8)
        btn_frame.pack(pady=(0, 10))
        
        # Auto-size and center
        DialogManager.auto_size_and_center(dialog, parent)
        
        dialog.wait_window()
        return result["confirmed"]


class ValidationHelper:
    """Common validation utilities"""
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        if not date_str.strip():
            return True  # Empty is valid
        try:
            datetime.date.fromisoformat(date_str.strip())
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Optional[str]:
        """Validate required field, return error message if invalid"""
        if not value.strip():
            return f"{field_name} cannot be empty"
        return None


class FormBuilder:
    """Helper for building consistent forms"""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.row = 0
        self.fields = {}
    
    def add_text_field(self, label: str, initial_value: str = "", width: int = 40) -> tk.StringVar:
        """Add a text field to the form"""
        tk.Label(self.parent, text=f"{label}:").grid(
            row=self.row, column=0, sticky="e", padx=5, pady=2
        )
        var = tk.StringVar(value=initial_value)
        entry = tk.Entry(self.parent, textvariable=var, width=width)
        entry.grid(row=self.row, column=1, padx=5, pady=2, sticky="w")
        
        self.fields[label.lower().replace(" ", "_")] = var
        self.row += 1
        return var
    
    def add_combobox(self, label: str, values: list, initial_value: str = "") -> tk.StringVar:
        """Add a combobox field to the form"""
        from tkinter import ttk
        
        tk.Label(self.parent, text=f"{label}:").grid(
            row=self.row, column=0, sticky="e", padx=5, pady=2
        )
        var = tk.StringVar(value=initial_value)
        combo = ttk.Combobox(self.parent, textvariable=var, values=values, 
                           state="readonly", width=18)
        combo.grid(row=self.row, column=1, padx=5, pady=2, sticky="w")
        
        self.fields[label.lower().replace(" ", "_")] = var
        self.row += 1
        return var
    
    def add_button_row(self, buttons: list):
        """Add a row of buttons with tight spacing"""
        # Create a frame for buttons to control spacing better
        button_frame = tk.Frame(self.parent)
        button_frame.grid(row=self.row, column=0, columnspan=2, pady=8)
        
        # Reverse button order so Save appears left of Cancel
        reversed_buttons = list(buttons)
        
        for text, command in reversed_buttons:
            tk.Button(button_frame, text=text, command=command).pack(
                side=tk.LEFT, padx=5
            )
        self.row += 1
