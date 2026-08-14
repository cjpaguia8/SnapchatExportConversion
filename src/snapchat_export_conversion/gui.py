"""Friendly desktop interface for the photo conversion tools."""

from __future__ import annotations

import os
import queue
import tempfile
import threading
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from snapchat_export_conversion.convert import ConversionSummary, convert_files
from snapchat_export_conversion.snapchat import batch_unzip


@dataclass(frozen=True)
class RunRequest:
    """Validated selections for one GUI run."""

    media_input: Path | None
    zip_input: Path | None
    photo_output: Path | None
    merged_output: Path | None


@dataclass(frozen=True)
class RunResult:
    converted: int
    conversion_failures: int
    archives: int
    archive_failures: int

    @property
    def failures(self) -> int:
        return self.conversion_failures + self.archive_failures


def validate_selections(
    media_input: str,
    zip_input: str,
    photo_output: str,
    merged_output: str,
) -> RunRequest:
    """Validate GUI values and normalize them into paths."""
    media = Path(media_input).expanduser() if media_input.strip() else None
    archives = Path(zip_input).expanduser() if zip_input.strip() else None
    photos = Path(photo_output).expanduser() if photo_output.strip() else None
    merged = Path(merged_output).expanduser() if merged_output.strip() else None

    if media is None and archives is None:
        raise ValueError("Select at least one input folder.")
    if media is not None:
        if not media.is_dir():
            raise ValueError("The raw media input folder does not exist.")
        if photos is None:
            raise ValueError("Select an output folder for converted photos.")
    if archives is not None:
        if not archives.is_dir():
            raise ValueError("The Snapchat ZIP input folder does not exist.")
        if merged is None:
            raise ValueError("Select an output folder for merged Snapchat media.")
    return RunRequest(media, archives, photos, merged)


def conflicting_outputs(request: RunRequest) -> tuple[Path, ...]:
    """Return output files that would be replaced by this run."""
    conflicts: list[Path] = []
    if request.media_input and request.photo_output:
        for source in request.media_input.iterdir():
            candidate = request.photo_output / f"{source.stem}.jpg"
            if source.is_file() and candidate.exists():
                conflicts.append(candidate)
    if request.zip_input and request.merged_output:
        for archive in request.zip_input.glob("*.zip"):
            for suffix in (".jpg", ".mp4"):
                candidate = request.merged_output / f"{archive.stem}{suffix}"
                if candidate.exists():
                    conflicts.append(candidate)
    return tuple(conflicts)


def run_request(request: RunRequest, progress: Callable[[str], None]) -> RunResult:
    """Execute a validated request and report human-readable progress."""
    summary = ConversionSummary(0, 0, ())
    archive_count = archive_failures = 0
    if request.media_input and request.photo_output:
        progress("Converting raw media...")
        summary = convert_files(
            request.media_input, request.photo_output, progress=progress
        )
    if request.zip_input and request.merged_output:
        progress("Extracting and merging Snapchat archives...")
        archive_count = len(tuple(request.zip_input.glob("*.zip")))
        with tempfile.TemporaryDirectory(
            prefix="snapchat-export-conversion-"
        ) as temporary:
            archive_failures = batch_unzip(
                request.zip_input,
                temporary,
                request.merged_output,
                progress=progress,
            )
    return RunResult(
        summary.successful,
        len(summary.failed),
        archive_count,
        archive_failures,
    )


class SnapchatExportConversionApp:
    """Tkinter application for selecting folders and running conversions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snapchat Export Conversion")
        self.root.geometry("760x520")
        self.root.minsize(680, 480)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.variables = {
            "media_input": tk.StringVar(),
            "zip_input": tk.StringVar(),
            "photo_output": tk.StringVar(),
            "merged_output": tk.StringVar(),
        }
        self._build_interface()

    def _build_interface(self) -> None:
        outer = ttk.Frame(self.root, padding=24)
        outer.pack(fill="both", expand=True)
        ttk.Label(
            outer,
            text="Snapchat Export Conversion",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            outer,
            text=(
                "Choose one or both input types, then select where to save the results."
            ),
        ).pack(anchor="w", pady=(4, 20))

        form = ttk.Frame(outer)
        form.pack(fill="x")
        self._folder_row(form, 0, "Raw photos or media", "media_input")
        self._folder_row(form, 1, "Snapchat ZIP archives", "zip_input")
        ttk.Separator(form).grid(row=2, column=0, columnspan=3, sticky="ew", pady=14)
        self._folder_row(form, 3, "Converted photos", "photo_output")
        self._folder_row(form, 4, "Merged Snapchat media", "merged_output")
        form.columnconfigure(1, weight=1)

        self.run_button = ttk.Button(outer, text="Run Conversion", command=self.start)
        self.run_button.pack(anchor="e", pady=(22, 10))
        self.progress_bar = ttk.Progressbar(outer, mode="indeterminate")
        self.progress_bar.pack(fill="x")
        self.status = tk.StringVar(value="Ready")
        ttk.Label(outer, textvariable=self.status, wraplength=700).pack(
            anchor="w", pady=(8, 10)
        )

        self.results = ttk.Frame(outer)
        self.results.pack(fill="x", side="bottom")
        self.open_photos = ttk.Button(
            self.results,
            text="Open Converted Photos",
            command=lambda: self._open_selected("photo_output"),
        )
        self.open_merged = ttk.Button(
            self.results,
            text="Open Merged Media",
            command=lambda: self._open_selected("merged_output"),
        )

    def _folder_row(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        key: str,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(parent, textvariable=self.variables[key]).grid(
            row=row, column=1, sticky="ew", padx=10, pady=6
        )
        ttk.Button(parent, text="Browse...", command=lambda: self._browse(key)).grid(
            row=row, column=2, pady=6
        )

    def _browse(self, key: str) -> None:
        selected = filedialog.askdirectory(
            title="Select folder", initialdir=self.variables[key].get() or None
        )
        if selected:
            self.variables[key].set(selected)

    def start(self) -> None:
        try:
            request = validate_selections(
                *(self.variables[key].get() for key in self.variables)
            )
        except ValueError as exc:
            messagebox.showerror("Check your folder selections", str(exc))
            return

        conflicts = conflicting_outputs(request)
        if conflicts and not messagebox.askyesno(
            "Replace existing files?",
            f"This run will replace {len(conflicts)} existing output file(s). "
            "Continue?",
        ):
            return

        for output in (request.photo_output, request.merged_output):
            if output is not None:
                try:
                    output.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    messagebox.showerror("Could not create output folder", str(exc))
                    return

        self.run_button.configure(state="disabled")
        self.open_photos.pack_forget()
        self.open_merged.pack_forget()
        self.progress_bar.start(12)
        self.status.set("Starting...")
        threading.Thread(target=self._worker, args=(request,), daemon=True).start()
        self.root.after(100, self._poll_events)

    def _worker(self, request: RunRequest) -> None:
        try:
            result = run_request(
                request, lambda message: self.events.put(("progress", message))
            )
            self.events.put(("done", result))
        except Exception as exc:
            self.events.put(("error", exc))

    def _poll_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "progress":
                    self.status.set(str(payload))
                elif event == "done":
                    self._finish(payload)
                    return
                else:
                    self._fail(payload)
                    return
        except queue.Empty:
            self.root.after(100, self._poll_events)

    def _finish(self, payload: object) -> None:
        result = payload
        assert isinstance(result, RunResult)
        self.progress_bar.stop()
        self.run_button.configure(state="normal", text="Run Again")
        summary = (
            f"Done! Converted {result.converted} media file(s) and processed "
            f"{result.archives - result.archive_failures} archive(s)."
        )
        if result.failures:
            summary += f" {result.failures} item(s) failed."
        self.status.set(summary)
        if self.variables["photo_output"].get():
            self.open_photos.pack(side="left", padx=(0, 8))
        if self.variables["merged_output"].get():
            self.open_merged.pack(side="left")
        if result.failures:
            messagebox.showwarning("Completed with errors", summary)
        else:
            messagebox.showinfo("Conversion complete", summary)

    def _fail(self, payload: object) -> None:
        self.progress_bar.stop()
        self.run_button.configure(state="normal", text="Run Again")
        self.status.set("The run stopped because of an error.")
        messagebox.showerror("Conversion failed", str(payload))

    def _open_selected(self, key: str) -> None:
        path = self.variables[key].get()
        if path and Path(path).is_dir():
            os.startfile(path)  # type: ignore[attr-defined]


def main() -> int:
    root = tk.Tk()
    SnapchatExportConversionApp(root)
    root.mainloop()
    return 0
