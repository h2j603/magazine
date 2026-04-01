# Instagram Magazine Feed Generator

HTML/CSS 템플릿 + Playwright를 사용해 인스타그램 피드 이미지를 생성하는 도구입니다.

## 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

## 사용법

### CLI로 단일 이미지 생성

```bash
python generate.py --template feed_minimal \
  --title "좋은 글은 마음을 한 뼘 넓혀준다" \
  --body "어느 독자의 편지에서" \
  --size square

python generate.py --template feed_text_overlay \
  --title "봄이 오는 길목에서" \
  --body "따뜻한 바람이 불어오는 계절" \
  --image ./photos/spring.jpg \
  --category "ESSAY" \
  --size portrait
```

### JSON 설정으로 일괄 생성

```bash
python generate.py config.json
```

`sample/config_example.json` 참고.

## 템플릿

| 템플릿 | 설명 | 추천 용도 |
|--------|------|-----------|
| `feed_text_overlay` | 배경 이미지 위 반투명 오버레이 + 텍스트 | 감성 사진 + 글귀 |
| `feed_editorial` | 사진/텍스트 분리형 에디토리얼 | 아티클, 리뷰 |
| `feed_minimal` | 텍스트 중심 미니멀 | 인용구, 공지 |
| `feed_split` | 좌우 분할 | 인터뷰, 제품 소개 |

## 규격

| 이름 | 크기 | 비율 | 용도 |
|------|------|------|------|
| `square` | 1080x1080 | 1:1 | 피드 (기본) |
| `portrait` | 1080x1350 | 4:5 | 피드 세로형 |
| `story` | 1080x1920 | 9:16 | 스토리/릴스 |

## 커스터마이징

모든 템플릿 변수는 `--extra` 옵션(JSON)이나 config 파일에서 오버라이드할 수 있습니다:

```bash
python generate.py -t feed_minimal \
  --title "제목" \
  -e '{"bg_color": "#1a1a1a", "text_color": "#ffffff", "title_font_size": "72px"}'
```

주요 변수: `bg_color`, `text_color`, `accent_color`, `font_family`, `title_font`, `title_font_size`, `body_font_size`, `padding` 등.

커스텀 폰트는 `assets/fonts/`에 파일을 넣고 `custom_font_url` 경로를 지정하면 됩니다.
