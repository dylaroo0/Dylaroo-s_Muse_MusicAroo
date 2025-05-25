{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 8, "minor": 1, "revision": 11, "architecture": "x64", "modernui": 1 },
    "rect": [0.0, 0.0, 600.0, 350.0],
    "bglocked": 0,
    "defrect": [0.0, 0.0, 600.0, 350.0],
    "openrect": [100.0, 100.0, 700.0, 450.0],
    "gridsnaponopen": 0,
    "gridsnap": 1,
    "gridonopen": 1,
    "grid": [15.0, 15.0],
    "default_fontname": "Arial",
    "default_fontsize": 12.0,
    "default_fontface": 0,
    "boxes": [
      { "box": { "maxclass":"live.dial",      "numinlets":1,"numoutlets":1,"patching_rect":[50,50,30,30],   "parameter_name":"chords",      "parameter_longname":"Chords"           } },
      { "box": { "maxclass":"live.dial",      "numinlets":1,"numoutlets":1,"patching_rect":[100,50,30,30],  "parameter_name":"harmony",     "parameter_longname":"Harmony"          } },
      { "box": { "maxclass":"live.dial",      "numinlets":1,"numoutlets":1,"patching_rect":[150,50,30,30],  "parameter_name":"bass",        "parameter_longname":"Bass"             } },
      { "box": { "maxclass":"live.dial",      "numinlets":1,"numoutlets":1,"patching_rect":[200,50,30,30],  "parameter_name":"drums",       "parameter_longname":"Drums"            } },
      { "box": { "maxclass":"live.menu",      "numinlets":1,"numoutlets":1,"patching_rect":[50,100,120,20], "parameter_name":"style",       "parameter_longname":"Style",       "items":["Swing","Funk","Rock","Electronic"] } },
      { "box": { "maxclass":"live.menu",      "numinlets":1,"numoutlets":1,"patching_rect":[180,100,120,20],"parameter_name":"subdivision","parameter_longname":"Subdivision","items":["1","2","4","8","16"] } },
      { "box": { "maxclass":"live.toggle",    "numinlets":1,"numoutlets":1,"patching_rect":[310,100,20,20], "parameter_name":"match_clip", "parameter_longname":"Match Clip Length"  } },
      { "box": { "maxclass":"live.button",    "numinlets":1,"numoutlets":1,"patching_rect":[50,150,20,20]                                                       } },
      { "box": { "maxclass":"pack",           "numinlets":7,"numoutlets":1,"patching_rect":[100,150,150,20],  "text":"pack 0 0 0 0 0 0 0"                 } },
      { "box": { "maxclass":"message",        "numinlets":1,"numoutlets":1,"patching_rect":[260,150,150,20],  "text":"prepend drummaroo"                   } },
      { "box": { "maxclass":"live.thisdevice","numinlets":1,"numoutlets":1,"patching_rect":[260,180,100,20]                                       } }
    ],
    "lines": [
      { "patchline": { "source":[0,0], "destination":[8,0] } },
      { "patchline": { "source":[1,0], "destination":[8,1] } },
      { "patchline": { "source":[2,0], "destination":[8,2] } },
      { "patchline": { "source":[3,0], "destination":[8,3] } },
      { "patchline": { "source":[4,0], "destination":[8,4] } },
      { "patchline": { "source":[5,0], "destination":[8,5] } },
      { "patchline": { "source":[6,0], "destination":[8,6] } },
      { "patchline": { "source":[7,0], "destination":[9,0] } },
      { "patchline": { "source":[8,0], "destination":[9,0] } },
      { "patchline": { "source":[9,0], "destination":[10,0] } }
    ]
  }
}
