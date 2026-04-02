#!/usr/bin/env python3
"""
Instagram Magazine Feed Image Generator

HTML/CSS 템플릿 + Playwright를 사용해 인스타그램 피드 이미지를 생성합니다.
폰트: 영문 Helvetica / 한글 Pretendard (CDN)

사용법:
    python generate.py config.json
    python generate.py --template cover --title "제목" --image photo.jpg

지원 규격:
    - portrait: 1080 x 1350 (기본, 4:5 세로형 피드)
    - square:   1080 x 1080 (정사각형 피드)
    - story:    1080 x 1920 (스토리/릴스)

템플릿 (캐러셀 매거진용):
    - cover:   표지 (이미지+검정 그라디언트+흰색 타이틀)
    - article: 본문 (에디토리얼 텍스트 페이지)
    - quote:   인용구 (미니멀 타이포그래피)
    - photo:   사진+캡션 (풀이미지+하단캡션 or 오버레이)
    - ending:  마무리/CTA (팔로우/저장 유도)
"""

import argparse
import json
import os
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

# 인스타그램 규격 프리셋
SIZE_PRESETS = {
    "square":   (1080, 1080),
    "portrait": (1080, 1350),
    "story":    (1080, 1920),
}

TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"


def _unescape_newlines(context: dict) -> dict:
    """CLI에서 전달된 리터럴 \\n을 실제 줄바꿈으로 변환합니다."""
    result = {}
    for k, v in context.items():
        if isinstance(v, str):
            result[k] = v.replace("\\n", "\n")
        else:
            result[k] = v
    return result


def render_html(template_name: str, context: dict) -> str:
    """Jinja2 템플릿을 렌더링하여 HTML 문자열을 반환합니다."""
    context = _unescape_newlines(context)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template(f"{template_name}.html")
    return template.render(**context)


def resolve_image_path(image_path: str | None) -> str | None:
    """이미지 경로를 file:// URI로 변환합니다."""
    if not image_path:
        return None
    p = Path(image_path).resolve()
    if not p.exists():
        print(f"[경고] 이미지 파일을 찾을 수 없습니다: {p}")
        return None
    return p.as_uri()


def generate_image(
    template_name: str,
    context: dict,
    output_path: str | None = None,
    size: str = "portrait",
    scale: int = 1,
) -> Path:
    """
    HTML 템플릿을 렌더링하고 Playwright로 스크린샷을 찍어 이미지를 생성합니다.

    Args:
        template_name: 사용할 템플릿 이름 (확장자 제외)
        context: 템플릿에 전달할 데이터 (title, body, image 등)
        output_path: 출력 파일 경로 (None이면 자동 생성)
        size: 이미지 규격 (portrait, square, story)
        scale: 배율 (2 = Retina 품질)

    Returns:
        생성된 이미지 파일 경로
    """
    width, height = SIZE_PRESETS.get(size, SIZE_PRESETS["portrait"])

    # 이미지 경로 처리
    if "image" in context and context["image"]:
        context["image"] = resolve_image_path(context["image"])

    # 커스텀 폰트 경로 처리
    if "custom_font_url" in context and context["custom_font_url"]:
        font_path = Path(context["custom_font_url"]).resolve()
        if font_path.exists():
            context["custom_font_url"] = font_path.as_uri()

    # 템플릿 컨텍스트에 크기 정보 추가
    context["width"] = width
    context["height"] = height

    html_content = render_html(template_name, context)

    # 출력 경로 설정
    if output_path is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = OUTPUT_DIR / f"{template_name}_{size}.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Playwright로 스크린샷
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        page.set_content(html_content, wait_until="domcontentloaded")
        # Pretendard CDN 등 외부 리소스 로딩 대기 (최대 8초, 실패해도 계속 진행)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        page.screenshot(path=str(output_path), full_page=False)
        browser.close()

    print(f"[완료] 이미지 생성: {output_path} ({width}x{height}, {scale}x)")
    return output_path


def generate_from_config(config_path: str) -> list[Path]:
    """JSON 설정 파일로부터 여러 이미지를 일괄 생성합니다."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 전역 설정
    defaults = config.get("defaults", {})
    results = []

    for i, slide in enumerate(config.get("slides", [])):
        # 전역 기본값과 개별 슬라이드 설정 병합
        ctx = {**defaults, **slide}
        template = ctx.pop("template", "cover")
        size = ctx.pop("size", "portrait")
        scale = ctx.pop("scale", 1)
        output = ctx.pop("output", None)

        if output is None:
            OUTPUT_DIR.mkdir(exist_ok=True)
            output = str(OUTPUT_DIR / f"slide_{i+1:02d}_{template}.png")

        result = generate_image(template, ctx, output_path=output, size=size, scale=scale)
        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="인스타그램 매거진 피드 이미지 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # JSON 설정 파일로 캐러셀 일괄 생성
  python generate.py carousel.json

  # CLI 옵션으로 단일 이미지 생성
  python generate.py --template cover \\
    --title "봄의 시작" \\
    --image ./photos/spring.jpg \\
    --category "ESSAY"

  # 추가 변수 전달
  python generate.py -t quote \\
    --title "좋은 글은 마음을 넓혀준다" \\
    -e '{"source": "어느 독자", "bg_color": "#1a1a1a", "text_color": "#fff"}'

캐러셀 매거진 템플릿:
  cover    표지 (이미지+검정 그라디언트+흰색 텍스트)
  article  본문 (에디토리얼 텍스트 페이지)
  quote    인용구 (미니멀 타이포그래피)
  photo    사진+캡션 (풀이미지+캡션바 또는 오버레이)
  ending   마무리/CTA (팔로우·저장 유도)

레거시 템플릿 (단일 피드용):
  feed_text_overlay  배경 이미지 위에 텍스트 오버레이
  feed_editorial     사진 + 텍스트 분리형 에디토리얼
  feed_minimal       텍스트 중심 미니멀 레이아웃
  feed_split         좌우(또는 상하) 분할 레이아웃

이미지 규격:
  portrait  1080x1350  4:5 세로형 (기본, 피드 최대 점유)
  square    1080x1080  정사각형
  story     1080x1920  스토리/릴스 9:16
        """,
    )

    parser.add_argument("config", nargs="?", help="JSON 설정 파일 경로")
    parser.add_argument("--template", "-t", default="cover", help="템플릿 이름")
    parser.add_argument("--title", help="제목 텍스트")
    parser.add_argument("--body", "-b", help="본문 텍스트")
    parser.add_argument("--image", "-i", help="배경/메인 이미지 경로")
    parser.add_argument("--category", help="카테고리 라벨")
    parser.add_argument("--author", help="저자/출처")
    parser.add_argument("--size", "-s", default="portrait", choices=SIZE_PRESETS.keys(), help="이미지 규격 (기본: portrait)")
    parser.add_argument("--scale", type=int, default=1, help="배율 (2=Retina)")
    parser.add_argument("--output", "-o", help="출력 파일 경로")
    parser.add_argument("--extra", "-e", help="추가 템플릿 변수 (JSON 문자열)")

    args = parser.parse_args()

    # JSON 설정 파일 모드
    if args.config:
        if not os.path.exists(args.config):
            print(f"[에러] 설정 파일을 찾을 수 없습니다: {args.config}")
            sys.exit(1)
        generate_from_config(args.config)
        return

    # CLI 모드 - title 또는 body 필수
    if not args.title and not args.body:
        parser.print_help()
        print("\n[에러] --title 또는 --body 중 하나는 필수입니다.")
        sys.exit(1)

    context = {}
    for key in ("title", "body", "image", "category", "author"):
        val = getattr(args, key)
        if val:
            context[key] = val

    # 추가 변수 병합
    if args.extra:
        extra = json.loads(args.extra)
        context.update(extra)

    generate_image(
        template_name=args.template,
        context=context,
        output_path=args.output,
        size=args.size,
        scale=args.scale,
    )


if __name__ == "__main__":
    main()
