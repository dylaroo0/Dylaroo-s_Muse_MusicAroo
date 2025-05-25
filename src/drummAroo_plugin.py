#!/usr/bin/env python3
import argparse
import os
import pretty_midi

def make_test_midi(out_path: str,
                   bars: int,
                   subdivision: int,
                   tempo: float = 120.0,
                   swing: float = 0.0,
                   velocity: int = 100):
    """
    Generate a simple drum pattern:
      - Kick on downbeats (every bar, beat 1)
      - Snare on beat 3 of each bar
      - Hi-hat on every subdivision
    """
    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    drum = pretty_midi.Instrument(program=0, is_drum=True, name='DrumKit')

    beats_per_bar = 4
    ticks_per_beat = subdivision
    seconds_per_beat = 60.0 / tempo
    subdiv_duration = seconds_per_beat / subdivision

    for bar in range(bars):
        # Kick on beat 1
        start = (bar * beats_per_bar + 0) * seconds_per_beat
        note = pretty_midi.Note(velocity=velocity, pitch=36, start=start, end=start+0.1)
        drum.notes.append(note)
        # Snare on beat 3
        start = (bar * beats_per_bar + 2) * seconds_per_beat
        note = pretty_midi.Note(velocity=velocity, pitch=38, start=start, end=start+0.1)
        drum.notes.append(note)
        # Hi-hat on every subdivision
        for i in range(beats_per_bar * subdivision):
            start = (bar * beats_per_bar * seconds_per_beat) + i * subdiv_duration
            note = pretty_midi.Note(velocity=int(velocity * 0.7), pitch=42,
                                     start=start, end=start + subdiv_duration * 0.9)
            drum.notes.append(note)

    pm.instruments.append(drum)
    pm.write(out_path)

def run_ml_model(args, out_path: str):
    """
    TODO: insert your trained model inference here.
    For now, just call test mode.
    """
    make_test_midi(out_path, args.length_bars, args.subdivision,
                   tempo=args.tempo_bpm, swing=args.swing, velocity=100)

def parse_args():
    p = argparse.ArgumentParser(prog='drummaroo_plugin.py')
    # Generators toggles
    p.add_argument('--chords',      type=int,   choices=[0,1], default=1)
    p.add_argument('--harmony',     type=int,   choices=[0,1], default=1)
    p.add_argument('--bass',        type=int,   choices=[0,1], default=1)
    p.add_argument('--drums',       type=int,   choices=[0,1], default=1)
    # Parameters
    p.add_argument('--style',       type=float, default=0.5)
    p.add_argument('--swing',       type=float, default=0.0)
    p.add_argument('--syncopation', type=float, default=0.0)
    p.add_argument('--wildness',    type=float, default=0.5)
    p.add_argument('--calmness',    type=float, default=0.5)
    p.add_argument('--humanize',    type=float, default=0.0)
    p.add_argument('--velocityJitter', type=float, default=0.0)
    # Subdivision and length
    p.add_argument('--subdivision', type=int, choices=[1,2,3], default=2,
                   help="1=8th, 2=16th, 3=32nd")
    p.add_argument('--matchLength', type=int, choices=[0,1], default=1)
    p.add_argument('--length_bars', type=int, default=4)
    # Tempo (if you want to override)
    p.add_argument('--tempo_bpm', type=float, default=120.0)
    # I/O
    p.add_argument('--input',    type=str, required=False,
                   help="Path to input MIDI/WAV (optional)")
    p.add_argument('--out_dir',  type=str, required=True,
                   help="Directory to write generated MIDI")
    p.add_argument('--test_mode', action='store_true',
                   help="Smoke-test stub (no ML)")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, 'generated.mid')

    if args.test_mode:
        make_test_midi(out_path, args.length_bars, args.subdivision,
                       tempo=args.tempo_bpm, swing=args.swing)
    else:
        run_ml_model(args, out_path)

    # Tell Max where to find it
    print(out_path)

if __name__ == '__main__':
    main()
