{
  "patcher": {
    "fileversion": 1,
    "rect": [0.0, 0.0, 800.0, 600.0],
    "bglocked": 0,
    "defrect": [0.0, 0.0, 800.0, 600.0],
    "openrect": [100.0, 100.0, 900.0, 700.0],
    "default_fontsize": 12.0,
    "default_fontface": 0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [15.0, 15.0],
    "boxes": [
      { "box": { "maxclass": "live.dial",   "numinlets": 1, "numoutlets": 1, "patching_rect": [50, 50, 30, 30],  "parameter_longname": "Chords",           "parameter_name": "chords",           "parameter_enable": 1 } },
      { "box": { "maxclass": "live.dial",   "numinlets": 1, "numoutlets": 1, "patching_rect": [100, 50, 30, 30], "parameter_longname": "Harmony",          "parameter_name": "harmony",          "parameter_enable": 1 } },
      { "box": { "maxclass": "live.dial",   "numinlets": 1, "numoutlets": 1, "patching_rect": [150, 50, 30, 30], "parameter_longname": "Bass",             "parameter_name": "bass",             "parameter_enable": 1 } },
      { "box": { "maxclass": "live.dial",   "numinlets": 1, "numoutlets": 1, "patching_rect": [200, 50, 30, 30], "parameter_longname": "Drums",            "parameter_name": "drums",            "parameter_enable": 1 } },
      { "box": { "maxclass": "live.menu",   "numinlets": 1, "numoutlets": 1, "patching_rect": [50, 100, 100, 20], "parameter_longname": "Style",            "parameter_name": "style",            "parameter_enable": 1, "items": ["Swing","Funk","Rock","Electronic"] } },
      { "box": { "maxclass": "live.menu",   "numinlets": 1, "numoutlets": 1, "patching_rect": [160, 100, 100, 20],"parameter_longname": "Subdivision",      "parameter_name": "subdivision",      "parameter_enable": 1, "items": ["1","2","4","8","16"] } },
      { "box": { "maxclass": "live.toggle", "numinlets": 1, "numoutlets": 1, "patching_rect": [270, 100, 20, 20], "parameter_longname": "Match Clip Length","parameter_name": "match_clip",      "parameter_enable": 1 } },
      { "box": { "maxclass": "live.button", "numinlets": 1, "numoutlets": 1, "patching_rect": [50, 150, 20, 20] } },
      { "box": { "maxclass": "message",     "numinlets": 2, "numoutlets": 1, "patching_rect": [100, 150, 350, 20],"text": "dict.pack chords $1 harmony $2 bass $3 drums $4 style $5 subdivision $6 match $7" } },
      { "box": { "maxclass": "prepend",     "numinlets": 2, "numoutlets": 1, "patching_rect": [100, 180, 150, 20],"text": "prepend drummaroo" } },
      { "box": { "maxclass": "live.thisdevice","numinlets": 1,"numoutlets": 1, "patching_rect": [100, 210, 100, 20] } }
    ],
    "lines": [
      { "patchline": { "source": [0, 0], "destination": [8, 0] } },
      { "patchline": { "source": [1, 0], "destination": [8, 1] } },
      { "patchline": { "source": [2, 0], "destination": [8, 2] } },
      { "patchline": { "source": [3, 0], "destination": [8, 3] } },
      { "patchline": { "source": [4, 0], "destination": [8, 4] } },
      { "patchline": { "source": [5, 0], "destination": [8, 5] } },
      { "patchline": { "source": [6, 0], "destination": [8, 6] } },
      { "patchline": { "source": [7, 0], "destination": [8, 0] } },
      { "patchline": { "source": [8, 0], "destination": [9, 1] } },
      { "patchline": { "source": [9, 0], "destination": [10, 0] } }
    ]
  }
}
