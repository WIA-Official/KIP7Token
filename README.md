# 교보문고 EPUB 2.0 생성기

WordPress 기사를 교보문고 호환 EPUB 2.0으로 변환하는 Python 스크립트

## ✨ 주요 기능

- ✅ **EPUBCheck 통과**: RSC-005, RSC-006 에러 완전 해결
- ✅ **교보문고 호환**: 교보문고 업로드 가능
- ✅ **BeautifulSoup 기반**: 안정적인 HTML 파싱
- ✅ **완벽한 정리**:
  - 테이블 → 순수 텍스트 변환
  - 이미지 완전 제거
  - 모든 HTML 속성 제거
  - script, style 태그 제거
- ✅ **XHTML 1.1 엄격 준수**

## 📁 파일 구조

```
.
├── epub_generator.py    # 메인 스크립트
├── test_data.json       # 테스트 데이터
├── requirements.txt     # 필요 패키지
└── README.md           # 이 파일
```

## 🚀 설치

```bash
# Python 3.6 이상 필요
pip install -r requirements.txt
```

필요한 패키지: `beautifulsoup4`

## 📖 사용법

### 1. JSON 데이터 준비

```json
{
  "articles": [
    {
      "title": "기사 제목",
      "content": "<p>HTML 내용...</p>",
      "author": "작가 이름",
      "date": "2024-11-14"
    }
  ],
  "options": {
    "author_name": "작가 이름",
    "title": "책 제목",
    "publisher": "출판사"
  }
}
```

### 2. EPUB 생성

```bash
python epub_generator.py input.json output.epub
```

### 3. 테스트

```bash
python epub_generator.py test_data.json test_output.epub
```

## 🔍 검증

생성된 EPUB 파일을 다음 사이트에서 검증:
- https://www.pagina.gmbh/produkte/epub-checker/

**목표: 에러 0개 ✅**

## 🛠️ 작동 원리

1. **HTML 파싱**: BeautifulSoup으로 안전하게 파싱
2. **정리 과정**:
   - script, style, noscript 태그 제거
   - 이미지 완전 제거
   - 테이블 → 텍스트 변환 (셀을 `|`로 구분)
   - 모든 HTML 속성 제거
   - 링크는 텍스트만 남김
3. **텍스트 추출**: 순수 텍스트로 변환
4. **XHTML 생성**: 가장 단순한 XHTML 1.1 생성
5. **EPUB 패키징**: EPUB 2.0 표준 준수

## ✅ 해결된 문제

### 이전 문제들:
- ❌ RSC-005: 허용되지 않는 속성 (border, align, decoding 등)
- ❌ RSC-006: 허용되지 않는 요소 (테이블 속성 등)
- ❌ 이미지 링크 깨짐
- ❌ 교보문고 "지원하지 않는 형식" 에러

### 현재 상태:
- ✅ 모든 검증 통과
- ✅ 교보문고 업로드 가능
- ✅ 순수 텍스트 기반 EPUB

## 📝 예제 출력

```
📚 EPUB 생성 시작: 5개 기사
📄 5개 챕터 생성 중...
   5/5 처리 중...
🗜️  EPUB 압축 중...

✅ EPUB 생성 완료!
   파일: test_output.epub
   크기: 12,345 bytes
   기사: 5개

🔍 검증: https://www.pagina.gmbh/produkte/epub-checker/

✨ SUCCESS
```

## 🤝 기여

버그 리포트 및 개선 제안 환영합니다!

## 📄 라이선스

MIT License

## 🔗 참고

- [EPUB 2.0 명세](http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm)
- [XHTML 1.1](https://www.w3.org/TR/xhtml11/)
- [EPUBCheck](https://www.w3.org/publishing/epubcheck/)
- [교보문고](https://www.kyobobook.co.kr/)