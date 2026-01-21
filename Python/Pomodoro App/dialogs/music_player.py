import os
import sys
import vlc
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QComboBox
)



class music_player(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MusicPlayer")
        self.resize(300, 200)

        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        self._current_path = ""
        self._is_playing = False

        self.play = QPushButton("Play")
        self.pause = QPushButton("Pause")
        self.track_selection = QComboBox()
        self.track_selection.addItems(['Rain', 'River', 'Rain + Thunder', 'Brown Noise'])

        self.play.clicked.connect(self.on_play)
        self.pause.clicked.connect(self.on_pause)
        self.track_selection.currentIndexChanged.connect(self.on_track_changed)

        self.tracks = {
            "Rain": r"media/rain.mp3",
            "River": r"media/river.mp3",
            "Rain + Thunder": r"media/rain_thunder.mp3",
            "Brown Noise": r"media/brownnoise.mp3",
        }

        layout = QVBoxLayout()
        layout.addWidget(self.play)
        layout.addWidget(self.pause)
        layout.addWidget(self.track_selection)
        self.setLayout(layout)

    def resource_path(self, rel_path: str) -> str:
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, rel_path)

    def load_selected_track(self):
        if self._is_playing:
            self.vlc_player.stop()
            self._is_playing = False

        name = self.track_selection.currentText()
        rel = self.tracks[name].replace("\\", "/")
        path = os.path.abspath(self.resource_path(rel))

        media = self.vlc_instance.media_new(path)
        self.vlc_player.set_media(media)
        self._current_path = path

    def on_play(self):
        if not self._current_path:
            self.load_selected_track()
        self.vlc_player.set_pause(0)
        self.vlc_player.play()
        self._is_playing = True

    def on_pause(self):
        self.vlc_player.set_pause(1)
        self._is_playing = False

    def on_track_changed(self):
        was_playing = self._is_playing
        self.load_selected_track()
        if was_playing:
            self.vlc_player.play()
            self._is_playing = True
