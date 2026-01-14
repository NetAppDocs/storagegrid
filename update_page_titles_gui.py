#!/usr/bin/env python3
"""
StorageGRID Page Title Updater - GUI Tool

This tool helps update page titles in StorageGRID documentation to comply with
content standards, particularly ensuring product name inclusion.
"""

import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class PageTitleUpdater:
    """Main application for updating page titles."""
    
    FORBIDDEN_WORDS = [
        "guide", "manual", "primer", "book", "topic", "article",
        "how to", "task", "reference", "page", "concept", "considerations",
        "overview", "introduction"
    ]
    
    TASK_VERBS = [
        'add', 'adding',
        'apply', 'applying',
        'access', 'accessing',
        'backup', 'backing up',
        'change', 'changing',
        'check', 'checking',
        'collect', 'collecting',
        'configure', 'configuring',
        'copy', 'copying',
        'create', 'creating',
        'delete', 'deleting',
        'deploy', 'deploying',
        'disable', 'disabling',
        'download', 'downloading',
        'edit', 'editing',
        'enable', 'enabling',
        'expand', 'expanding',
        'gather', 'gathering',
        'install', 'installing',
        'maintain', 'maintaining',
        'manage', 'managing',
        'migrate', 'migrating',
        'monitor', 'monitoring',
        'move', 'moving',
        'perform', 'performing',
        'protect', 'protecting',
        'provision', 'provisioning',
        'rebalance', 'rebalancing',
        'remove', 'removing',
        'replicate', 'replicating',
        'restore', 'restoring',
        'review', 'reviewing',
        'run', 'running',
        'set up', 'setting up',
        'silence', 'silencing',
        'start', 'starting',
        'stop', 'stopping',
        'trigger', 'triggering',
        'troubleshoot', 'troubleshooting',
        'update', 'updating',
        'upgrade', 'upgrading',
        'use', 'using',
        'view', 'viewing'
    ]
    
    FOLDERS = [
        "admin", "audit", "expand", "fabricpool", "harden", "ilm",
        "maintain", "monitor", "network", "primer", "release-notes",
        "rhel", "s3", "swift", "swnodes", "tenant", "troubleshoot",
        "ubuntu", "upgrade", "vmware"
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("StorageGRID Page Title Updater")
        self.root.geometry("1400x900")
        
        # Get repository root
        self.repo_root = Path(__file__).parent
        
        # Current state
        self.current_folder = None
        self.files_data = []
        self.current_file_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Folder selection
        ttk.Label(main_frame, text="Select Folder:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        self.folder_var = tk.StringVar()
        folder_combo = ttk.Combobox(
            main_frame, textvariable=self.folder_var, values=self.FOLDERS, width=30
        )
        folder_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        folder_combo.bind("<<ComboboxSelected>>", self.on_folder_selected)
        
        ttk.Button(main_frame, text="Load Folder", command=self.load_folder).grid(
            row=0, column=2, pady=5, padx=5
        )
        
        # Statistics
        self.stats_label = ttk.Label(main_frame, text="No folder loaded", font=("Arial", 10))
        self.stats_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # File list and editor (split horizontally)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - File list
        list_frame = ttk.LabelFrame(content_frame, text="Files", padding="5")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # File listbox with scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.file_listbox = tk.Listbox(
            list_frame, width=40, yscrollcommand=list_scroll.set, font=("Courier", 9)
        )
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_scroll.config(command=self.file_listbox.yview)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_selected)
        
        # Right panel - Editor
        editor_frame = ttk.LabelFrame(content_frame, text="Title Editor", padding="5")
        editor_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(4, weight=1)
        
        # File info
        ttk.Label(editor_frame, text="File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.file_label = ttk.Label(editor_frame, text="", font=("Arial", 10, "italic"))
        self.file_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Current title
        ttk.Label(editor_frame, text="Current Title:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.current_title_label = ttk.Label(
            editor_frame, text="", wraplength=800, justify=tk.LEFT
        )
        self.current_title_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Lead paragraph (for context)
        ttk.Label(editor_frame, text="Lead:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=2)
        self.lead_label = ttk.Label(
            editor_frame, text="", wraplength=800, justify=tk.LEFT,
            foreground="#555", font=("Arial", 9, "italic")
        )
        self.lead_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Compliance status
        ttk.Label(editor_frame, text="Compliance:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.compliance_label = ttk.Label(editor_frame, text="", font=("Arial", 10))
        self.compliance_label.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Recommended title
        ttk.Label(editor_frame, text="Recommended:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        recommend_frame = ttk.Frame(editor_frame)
        recommend_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.recommended_label = ttk.Label(
            recommend_frame, text="", wraplength=750, justify=tk.LEFT,
            foreground="blue", font=("Arial", 10)
        )
        self.recommended_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            recommend_frame, text="✓ Accept", command=self.accept_recommendation,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        # New title entry
        ttk.Label(editor_frame, text="New Title:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        self.new_title_text = scrolledtext.ScrolledText(
            editor_frame, height=3, width=80, wrap=tk.WORD, font=("Arial", 10)
        )
        self.new_title_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        self.new_title_text.bind("<KeyRelease>", self.on_title_changed)
        
        # New title info
        self.new_title_info = ttk.Label(editor_frame, text="", font=("Arial", 9))
        self.new_title_info.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Issues/warnings display
        issues_frame = ttk.LabelFrame(editor_frame, text="Issues & Suggestions", padding="5")
        issues_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        issues_frame.columnconfigure(0, weight=1)
        issues_frame.rowconfigure(0, weight=1)
        
        self.issues_text = scrolledtext.ScrolledText(
            issues_frame, height=8, wrap=tk.WORD, font=("Arial", 9), state=tk.DISABLED
        )
        self.issues_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Action buttons
        button_frame = ttk.Frame(editor_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="⬅ Previous", command=self.previous_file).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Skip", command=self.next_file).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="Update & Next ➡", command=self.update_and_next,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update All Compliant", command=self.update_all).pack(
            side=tk.LEFT, padx=5
        )
        
        # Progress
        ttk.Label(main_frame, text="Progress:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.progress_label = ttk.Label(main_frame, text="0/0")
        self.progress_label.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
    def on_folder_selected(self, event=None):
        """Handle folder selection from dropdown."""
        self.load_folder()
        
    def load_folder(self):
        """Load all .adoc files from selected folder."""
        folder = self.folder_var.get()
        if not folder:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return
            
        folder_path = self.repo_root / folder
        if not folder_path.exists():
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
            return
            
        self.current_folder = folder
        self.files_data = []
        
        # Find all .adoc files
        adoc_files = sorted(folder_path.glob("*.adoc"))
        
        for file_path in adoc_files:
            if file_path.name == "sidebar.yml":
                continue
                
            title, lead, issues = self.parse_file(file_path)
            compliant = self.check_compliance(title)
            recommended = self.generate_recommended_title(title)
            
            self.files_data.append({
                "path": file_path,
                "filename": file_path.name,
                "current_title": title,
                "lead": lead,
                "recommended_title": recommended,
                "new_title": "",
                "compliant": compliant,
                "issues": issues,
                "updated": False
            })
        
        self.update_file_list()
        self.update_stats()
        
        if self.files_data:
            self.current_file_index = 0
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(0)
            self.file_listbox.see(0)
            self.load_current_file()
            
    def parse_file(self, file_path: Path) -> Tuple[str, str, List[str]]:
        """Parse an .adoc file to extract the page title and lead."""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Find the page title (line starting with = )
            title_match = re.search(r'^= (.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                issues.append("No page title found")
                return "", "", issues
            
            # Find the lead paragraph (text after [.lead])
            lead = ""
            lead_match = re.search(r'\[\.lead\]\s*\n(.+?)(?=\n\n|\n\[|$)', content, re.DOTALL)
            if lead_match:
                lead = lead_match.group(1).strip()
                # Remove any AsciiDoc inline formatting for display
                lead = re.sub(r'`([^`]+)`', r'\1', lead)  # Remove backticks
                lead = re.sub(r'\*\*([^*]+)\*\*', r'\1', lead)  # Remove bold
                lead = re.sub(r'__([^_]+)__', r'\1', lead)  # Remove italic
                # Clean up any line breaks within the lead
                lead = ' '.join(lead.split())
            
            return title, lead, issues
                
        except Exception as e:
            issues.append(f"Error reading file: {e}")
            return "", "", issues
            
    def check_compliance(self, title: str) -> bool:
        """Check if a title complies with standards."""
        if not title:
            return False
            
        # Check for StorageGRID
        has_product = "StorageGRID" in title or "Grid Manager" in title or "Tenant Manager" in title
        
        # Check length
        length_ok = 30 <= len(title) <= 70
        
        # Check for forbidden words
        title_lower = title.lower()
        has_forbidden = any(word in title_lower for word in self.FORBIDDEN_WORDS)
        
        # Check for colons (not in code/URLs)
        has_colon = ":" in title and not title.startswith("http")
        
        return has_product and length_ok and not has_forbidden and not has_colon
    
    def generate_recommended_title(self, current_title: str) -> str:
        """
        Generate a recommended compliant title based on the current title.
        Follows NetApp documentation standards for StorageGRID:
        - Task titles: imperative command + purpose/result
        - Concept titles: "Learn about" + feature/capability + context
        """
        if not current_title:
            return ""
        
        title = current_title.strip()
        original_title = title
        
        # Step 1: Determine if this is a task or concept page
        # Task pages start with imperative verbs (configure, install, add, etc.)
        title_lower = title.lower()
        is_task = any(title_lower.startswith(verb) for verb in self.TASK_VERBS)
        
        # Also check for gerund forms that indicate tasks (e.g., "Configuring...")
        is_gerund_task = any(title_lower.startswith(verb + 'ing') for verb in [
            'add', 'configur', 'install', 'deploy', 'manag', 'monitor', 
            'upgrad', 'expand', 'troubleshoot', 'rebalanc', 'cop'
        ])
        
        if is_gerund_task and not is_task:
            # Convert gerund to imperative
            # "Configuring X" -> "Configure X"
            title = re.sub(r'^(\w+)ing\s+', lambda m: m.group(1).rstrip('e') + 'e ' if m.group(1).endswith('ur') 
                          else m.group(1) + ' ', title, flags=re.IGNORECASE)
            is_task = True
        
        # Step 2: Remove forbidden words and clean up patterns
        # Remove "considerations", "overview", "introduction", etc.
        title = re.sub(r'^Considerations for\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+considerations$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^Overview of\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^Introduction to\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+(overview|introduction|guide|manual|primer)$', '', title, flags=re.IGNORECASE)
        
        # For concept pages, remove "About" patterns (will be replaced with "Learn about")
        if not is_task:
            title = re.sub(r'^About the\s+', '', title, flags=re.IGNORECASE)
            title = re.sub(r'^About\s+', '', title, flags=re.IGNORECASE)
        
        # Remove "reference" patterns
        title = re.sub(r'\s+reference$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\breference\b', '', title, flags=re.IGNORECASE)
        
        # Remove "How to" prefix
        title = re.sub(r'^How to\s+', '', title, flags=re.IGNORECASE)
        
        # Clean up "the" after verbs (e.g., "View the X" -> "View X")
        title = re.sub(r'^(View|Use|Check|Verify|Monitor|Review)\s+the\s+', r'\1 ', title, flags=re.IGNORECASE)
        
        # Remove "steps" suffix for task pages
        if is_task:
            title = re.sub(r'\s+steps$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s+procedure$', '', title, flags=re.IGNORECASE)
        
        # Step 3: Add StorageGRID if not present
        has_product = "StorageGRID" in title or "Grid Manager" in title or "Tenant Manager" in title
        
        if not has_product:
            if is_task:
                # Task pattern: imperative verb + purpose/result + "in StorageGRID"
                # Examples from instructions:
                # - "Configure the NFS datastore... in VMware" (analogous)
                # - "Monitor on-premises storage with Data Infrastructure Insights"
                
                # Determine best preposition based on verb and context
                title_lower = title.lower()
                
                # Use "for StorageGRID" for preparation/planning verbs
                use_for = any(title_lower.startswith(verb) for verb in [
                    'gather', 'prepare', 'plan', 'design', 'select', 'choose'
                ])
                
                # Use "to StorageGRID" for adding/moving/copying operations
                use_to = any(title_lower.startswith(verb) for verb in [
                    'add', 'copy', 'move', 'migrate', 'replicate'
                ])
                
                if use_to:
                    # Check if already has a destination (e.g., "to expansion nodes")
                    if ' to ' not in title_lower:
                        title = f"{title} to StorageGRID"
                    else:
                        title = f"{title} in StorageGRID"
                elif use_for:
                    title = f"{title} for StorageGRID"
                else:
                    title = f"{title} in StorageGRID"
            else:
                # Concept pattern: "Learn about" + feature + "in StorageGRID"
                # Examples from instructions:
                # - "Learn about hybrid multi-cloud environments with NetApp..."
                # - "Learn about mitigating security and ransomware risks..."
                
                # Remove existing "Learn about" if present to avoid duplication
                title = re.sub(r'^Learn about\s+', '', title, flags=re.IGNORECASE)
                
                # Apply concept pattern
                title = f"Learn about {title.lower()} in StorageGRID"
        
        # Step 4: Ensure sentence case (capitalize first word and proper nouns only)
        title = self.apply_sentence_case(title)
        
        # Step 5: Clean up double words and extra spaces
        title = re.sub(r'\bthe\s+the\b', 'the', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()
        
        # Step 6: If title is too long (>70 chars), try to shorten
        if len(title) > 70:
            # Remove "the" to shorten
            title = re.sub(r'\bthe\s+', '', title, count=1, flags=re.IGNORECASE)
            
        if len(title) > 70:
            # Remove "a/an" to shorten further
            title = re.sub(r'\ban?\s+', '', title, count=1, flags=re.IGNORECASE)
            
        if len(title) > 70:
            # Try to condense common phrases
            title = title.replace(' operations', '')
            title = title.replace(' and system', '')
            title = title.replace(' configuration', '')
        
        # Ensure it starts with capital letter
        if title and title[0].islower():
            title = title[0].upper() + title[1:]
        
        return title.strip()
    
    def apply_sentence_case(self, title: str) -> str:
        """Apply sentence case: capitalize first word and proper nouns only."""
        if not title:
            return title
        
        # Proper nouns and acronyms that should stay capitalized
        proper_nouns = [
            'StorageGRID', 'Grid Manager', 'Tenant Manager', 'SNMP', 'NFS', 'CIFS',
            'S3', 'Swift', 'API', 'REST', 'HTTP', 'HTTPS', 'SSL', 'TLS',
            'AutoSupport', 'NetApp', 'ILM', 'NTP', 'DNS', 'LDAP', 'Active Directory',
            'SAMLassertML', 'Prometheus', 'Grafana', 'Linux', 'Windows', 'VMware',
            'AWS', 'Azure', 'GCP', 'TCP', 'IP', 'IPv4', 'IPv6', 'VLAN', 'BGP',
            'DHCP', 'NAT', 'VPN', 'SSH', 'FTP', 'SCP', 'SFTP', 'SMTP', 'IMAP',
            'POP3', 'SNMP', 'MIB', 'OID', 'CPU', 'RAM', 'SSD', 'HDD', 'RAID',
            'LUN', 'iSCSI', 'FC', 'FCoE', 'SAN', 'NAS', 'DAS'
        ]
        
        # First, lowercase everything
        result = title.lower()
        
        # Capitalize first character
        result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()
        
        # Restore proper nouns
        for noun in proper_nouns:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(noun.lower()) + r'\b'
            result = re.sub(pattern, noun, result, flags=re.IGNORECASE)
        
        return result
        
    def analyze_title(self, title: str) -> List[str]:
        """Analyze a title and return list of issues/suggestions."""
        if not title:
            return ["No title provided"]
            
        issues = []
        
        # Check product name
        if "StorageGRID" not in title and "Grid Manager" not in title and "Tenant Manager" not in title:
            issues.append("❌ Missing product name (StorageGRID, Grid Manager, or Tenant Manager)")
            
        # Check length
        length = len(title)
        if length < 30:
            issues.append(f"⚠️ Title too short: {length} characters (minimum 30)")
        elif length > 70:
            issues.append(f"⚠️ Title too long: {length} characters (maximum 70)")
        else:
            issues.append(f"✅ Length OK: {length} characters")
            
        # Check forbidden words
        title_lower = title.lower()
        found_forbidden = [word for word in self.FORBIDDEN_WORDS if word in title_lower]
        if found_forbidden:
            issues.append(f"❌ Contains forbidden words: {', '.join(found_forbidden)}")
        else:
            issues.append("✅ No forbidden words detected")
            
        # Check for colons
        if ":" in title:
            issues.append("❌ Contains colon (:) - not allowed in titles")
        else:
            issues.append("✅ No colons detected")
            
        # Check for special formatting
        if "`" in title or "*" in title or "_" in title:
            issues.append("❌ Contains special formatting (backticks, asterisks, underscores)")
        else:
            issues.append("✅ No special formatting detected")
            
        # Check capitalization (sentence case)
        if title[0].islower():
            issues.append("⚠️ Should start with capital letter")
        else:
            issues.append("✅ Starts with capital letter")
        
        # Check if it follows task or concept pattern
        is_task = any(title_lower.startswith(verb) for verb in self.TASK_VERBS)
        is_concept = title_lower.startswith("learn about")
        
        if is_task:
            issues.append("ℹ️ Detected as task-based title (imperative verb)")
        elif is_concept:
            issues.append("ℹ️ Detected as concept-based title (Learn about pattern)")
        else:
            issues.append("ℹ️ Title structure unclear - consider task or concept pattern")
            
        return issues
        
    def update_file_list(self):
        """Update the file listbox display."""
        self.file_listbox.delete(0, tk.END)
        
        for data in self.files_data:
            status = "✅" if data["compliant"] else "❌"
            update_mark = "📝" if data["updated"] else "  "
            display = f"{status} {update_mark} {data['filename']}"
            self.file_listbox.insert(tk.END, display)
            
    def update_stats(self):
        """Update statistics display."""
        total = len(self.files_data)
        compliant = sum(1 for d in self.files_data if d["compliant"])
        updated = sum(1 for d in self.files_data if d["updated"])
        
        stats_text = (
            f"Folder: {self.current_folder} | "
            f"Total: {total} | "
            f"Compliant: {compliant} ({compliant/total*100:.1f}%) | "
            f"Updated: {updated}"
        )
        self.stats_label.config(text=stats_text)
        
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = updated
        self.progress_label.config(text=f"{updated}/{total} files updated")
        
    def on_file_selected(self, event=None):
        """Handle file selection from listbox."""
        selection = self.file_listbox.curselection()
        if selection:
            self.current_file_index = selection[0]
            self.load_current_file()
            
    def load_current_file(self):
        """Load the current file into the editor."""
        if not self.files_data:
            return
            
        data = self.files_data[self.current_file_index]
        
        self.file_label.config(text=data["filename"])
        self.current_title_label.config(text=data["current_title"])
        
        # Display the lead paragraph for context
        lead_text = data.get("lead", "")
        if lead_text:
            # Truncate if too long for display
            if len(lead_text) > 300:
                lead_text = lead_text[:300] + "..."
            self.lead_label.config(text=lead_text)
        else:
            self.lead_label.config(text="(No lead paragraph found)")
        
        # Set compliance status
        if data["compliant"]:
            self.compliance_label.config(text="✅ COMPLIANT", foreground="green")
        else:
            self.compliance_label.config(text="❌ NON-COMPLIANT", foreground="red")
        
        # Show recommended title
        self.recommended_label.config(text=data["recommended_title"])
        
        # Load new title (either previously edited, recommended, or current)
        if data["new_title"]:
            new_title = data["new_title"]
        elif not data["compliant"]:
            new_title = data["recommended_title"]
        else:
            new_title = data["current_title"]
            
        self.new_title_text.delete("1.0", tk.END)
        self.new_title_text.insert("1.0", new_title)
        
        self.update_title_analysis()
    
    def accept_recommendation(self):
        """Accept the recommended title."""
        if not self.files_data:
            return
            
        data = self.files_data[self.current_file_index]
        recommended = data["recommended_title"]
        
        self.new_title_text.delete("1.0", tk.END)
        self.new_title_text.insert("1.0", recommended)
        self.update_title_analysis()
        
    def on_title_changed(self, event=None):
        """Handle changes to the new title text."""
        self.update_title_analysis()
        
    def update_title_analysis(self):
        """Update the analysis of the new title."""
        new_title = self.new_title_text.get("1.0", tk.END).strip()
        
        if new_title:
            issues = self.analyze_title(new_title)
            
            self.issues_text.config(state=tk.NORMAL)
            self.issues_text.delete("1.0", tk.END)
            self.issues_text.insert("1.0", "\n".join(issues))
            self.issues_text.config(state=tk.DISABLED)
            
            # Update info
            length = len(new_title)
            has_product = "StorageGRID" in new_title or "Grid Manager" in new_title or "Tenant Manager" in new_title
            compliant = self.check_compliance(new_title)
            
            info_text = f"Length: {length} chars | Has product name: {'Yes' if has_product else 'No'} | Compliant: {'Yes ✅' if compliant else 'No ❌'}"
            self.new_title_info.config(text=info_text)
        else:
            self.issues_text.config(state=tk.NORMAL)
            self.issues_text.delete("1.0", tk.END)
            self.issues_text.config(state=tk.DISABLED)
            self.new_title_info.config(text="")
            
    def previous_file(self):
        """Go to previous file."""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_file_index)
            self.file_listbox.see(self.current_file_index)
            self.load_current_file()
            
    def next_file(self):
        """Go to next file."""
        if self.current_file_index < len(self.files_data) - 1:
            self.current_file_index += 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_file_index)
            self.file_listbox.see(self.current_file_index)
            self.load_current_file()
            
    def update_and_next(self):
        """Update current file and move to next."""
        if not self.update_current_file():
            return
            
        self.next_file()
        
    def update_current_file(self) -> bool:
        """Update the current file with new title."""
        if not self.files_data:
            return False
            
        data = self.files_data[self.current_file_index]
        new_title = self.new_title_text.get("1.0", tk.END).strip()
        
        if not new_title:
            messagebox.showwarning("No Title", "Please enter a new title.")
            return False
            
        if new_title == data["current_title"]:
            messagebox.showinfo("No Change", "Title is unchanged.")
            return False
            
        try:
            # Read file
            with open(data["path"], "r", encoding="utf-8") as f:
                content = f.read()
                
            # Replace title
            old_title_pattern = re.escape(data["current_title"])
            new_content = re.sub(
                rf'^= {old_title_pattern}$',
                f'= {new_title}',
                content,
                count=1,
                flags=re.MULTILINE
            )
            
            # Write back
            with open(data["path"], "w", encoding="utf-8") as f:
                f.write(new_content)
                
            # Update data
            data["new_title"] = new_title
            data["current_title"] = new_title
            data["compliant"] = self.check_compliance(new_title)
            data["updated"] = True
            
            self.update_file_list()
            self.update_stats()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update file: {e}")
            return False
            
    def update_all(self):
        """Update all files where new title is compliant."""
        if not messagebox.askyesno(
            "Confirm Bulk Update",
            "Update all files with compliant new titles?\n\n"
            "This will update multiple files at once."
        ):
            return
            
        updated_count = 0
        
        for i, data in enumerate(self.files_data):
            if data["updated"]:
                continue
                
            # For now, skip auto-update - user should review each
            # In future, could implement suggestions
            
        messagebox.showinfo("Update Complete", f"Updated {updated_count} files.")
        self.update_stats()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = PageTitleUpdater(root)
    root.mainloop()


if __name__ == "__main__":
    main()
