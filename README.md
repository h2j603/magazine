# Instagram Magazine Feed Generator

HTML/CSS 템플릿 + Playwright 기반 인스타그램 매거진 캐러셀 이미지 생성기.

- **폰트**: 영문 Helvetica / 한글 Pretendard (CDN)
- **기본 규격**: 1080x1350 (4:5 세로형, 피드 최대 점유율)
- **캐러셀 매거진 구조**: 표지 → 본문 → 인용 → 사진 → 마무리

## 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

## 사용법

### 캐러셀 일괄 생성 (JSON config)

```bash
python generate.py carousel.json
```

`sample/config_example.json` 참고:

```json
{
  "defaults": {
    "size": "portrait",
    "magazine_name": "YOUR MAGAZINE"
  },
  "slides": [
    { "template": "cover",   "title": "제목", "image": "./photo.jpg", "category": "ESSAY" },
    { "template": "article", "heading": "소제목", "body": "본문 텍스트..." },
    { "template": "quote",   "text": "인용구", "source": "출처" },
    { "template": "ending",  "message": "저장하고 공유해 주세요", "cta_text": "FOLLOW" }
  ]
}
```

### CLI 단일 이미지 생성

```bash
# 표지
python generate.py -t cover --title "봄의 시작" --image photo.jpg --category "ESSAY"

# 인용구 (다크 모드)
python generate.py -t quote --title "x" \
  -e '{"text": "좋은 글은 마음을 넓혀준다", "source": "독자", "bg_color": "#1a1a1a", "text_color": "#fff"}'
```

## 캐러셀 매거진 템플릿

| 템플릿 | 설명 | 슬라이드 위치 |
|--------|------|--------------|
| `cover` | 이미지 + 검정 그라디언트 + 흰색 타이틀 | 첫 번째 (표지) |
| `article` | 에디토리얼 텍스트 페이지 (선택적 상단 이미지) | 본문 |
| `quote` | 미니멀 인용구 + 출처 | 중간 브레이크 |
| `photo` | 풀 이미지 + 캡션바 또는 오버레이 | 사진 중심 |
| `ending` | 매거진명 + CTA (팔로우/저장 유도) | 마지막 |

## 이미지 규격

| 이름 | 크기 | 비율 | 용도 |
|------|------|------|------|
| `portrait` | 1080x1350 | 4:5 | 피드 세로형 (기본) |
| `square` | 1080x1080 | 1:1 | 피드 정사각형 |
| `story` | 1080x1920 | 9:16 | 스토리/릴스 |

## 커스터마이징

`--extra`(JSON) 또는 config 파일에서 모든 CSS 변수를 오버라이드 가능:

`bg_color`, `text_color`, `accent_color`, `title_font_size`, `padding`, `gradient` 등.

커스텀 폰트는 `assets/fonts/`에 넣고 `custom_font_url` 지정.
