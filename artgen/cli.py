import argparse
import json
import re
import sys
from pathlib import Path

from .data import load_dotenv
from .compose import compose
from .text import wall_label, artist_statement, essay, bio
from .prompts import image_prompt, video_prompt
from . import render as render_mod
from . import gallery


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")[:60]


def cmd_generate(args):
    out_root = Path(args.out)
    for i in range(args.count):
        seed = None if args.seed is None else args.seed + i
        spec = compose(seed=seed, kind=args.kind)
        slug = slugify(spec["title"])
        if seed is not None:
            slug = f"{seed:04d}-{slug}"
        out_dir = out_root / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        label = wall_label(spec)
        statement = artist_statement(spec)
        essay_md = essay(spec)
        if args.llm:
            from .llm import expand_essay
            print(f"  expanding essay with Claude ...", file=sys.stderr)
            essay_md = expand_essay(spec, essay_md)

        (out_dir / "spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
        (out_dir / "label.md").write_text(label + "\n", encoding="utf-8")
        (out_dir / "statement.md").write_text(statement + "\n", encoding="utf-8")
        (out_dir / "essay.md").write_text(essay_md + "\n", encoding="utf-8")
        (out_dir / "bio.md").write_text(bio(spec) + "\n", encoding="utf-8")

        ip = image_prompt(spec)
        vp = video_prompt(spec)
        (out_dir / "video_prompt.txt").write_text(vp + "\n", encoding="utf-8")

        media = None
        if not args.no_render:
            try:
                media = render_mod.render(spec, ip, out_dir, provider=args.provider, video=False)
                if args.video:
                    media = render_mod.render(spec, vp, out_dir, provider=args.provider, video=True)
            except render_mod.RenderError as e:
                print(f"  render failed: {e}", file=sys.stderr)
                media = render_mod.render_placeholder(spec, ip, out_dir)
        else:
            (out_dir / "image_prompt.txt").write_text(ip + "\n", encoding="utf-8")

        print(f"[{i+1}/{args.count}] {spec['artist']} — {spec['title']} ({spec['year']})")
        print(f"        {spec['form']}; {', '.join(spec['materials'])}")
        print(f"        -> {out_dir}" + (f"  media: {media.name}" if media else ""))

    if not args.no_gallery:
        page = gallery.build(out_root)
        print(f"gallery: {page}")


def cmd_show(args):
    spec = compose(seed=args.seed, kind=args.kind)
    print(wall_label(spec))
    print()
    print("## Artist statement\n")
    print(artist_statement(spec))
    print()
    print("## Curatorial essay\n")
    print(essay(spec))
    print()
    print("## Image prompt\n")
    print(image_prompt(spec))
    print()
    print("## Video prompt\n")
    print(video_prompt(spec))


def cmd_gallery(args):
    print(gallery.build(Path(args.out)))


def main(argv=None):
    p = argparse.ArgumentParser(prog="artgen", description="Randomly generate contemporary art and its discourse.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="generate works into an output folder, render media, build gallery")
    g.add_argument("-n", "--count", type=int, default=1)
    g.add_argument("--seed", type=int, default=None, help="base seed; work i uses seed+i")
    g.add_argument("--kind", choices=["video", "installation"], default=None)
    g.add_argument("--out", default="out")
    g.add_argument("--provider", choices=["dry", "fal", "replicate", "openai"], default=None)
    g.add_argument("--video", action="store_true", help="also render a video clip (fal/replicate)")
    g.add_argument("--llm", action="store_true", help="expand the essay with Claude (needs anthropic + credentials)")
    g.add_argument("--no-render", action="store_true", help="write prompts only")
    g.add_argument("--no-gallery", action="store_true")
    g.set_defaults(func=cmd_generate)

    s = sub.add_parser("show", help="print one work to stdout, no files")
    s.add_argument("--seed", type=int, default=None)
    s.add_argument("--kind", choices=["video", "installation"], default=None)
    s.set_defaults(func=cmd_show)

    ga = sub.add_parser("gallery", help="rebuild out/index.html")
    ga.add_argument("--out", default="out")
    ga.set_defaults(func=cmd_gallery)

    args = p.parse_args(argv)
    load_dotenv()
    args.func(args)


if __name__ == "__main__":
    main()
