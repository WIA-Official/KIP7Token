#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
교보문고 EPUB 2.0 생성기 - EPUBCheck 통과 버전
BeautifulSoup으로 완벽한 텍스트 추출
테이블, 이미지, 모든 속성 제거
"""

import os
import sys
import json
import zipfile
import re
from datetime import datetime
import uuid
from html import escape
import tempfile
import shutil

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ BeautifulSoup4가 필요합니다: pip install beautifulsoup4")
    sys.exit(1)


def extract_table_text(table):
    """테이블을 순수 텍스트로 변환"""
    lines = []
    rows = table.find_all('tr')

    for row in rows:
        cells = row.find_all(['td', 'th'])
        if cells:
            # 셀 내용을 공백으로 구분
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            line = ' | '.join(filter(None, cell_texts))
            if line:
                lines.append(line)

    return '\n'.join(lines)


def html_to_pure_text(html_content):
    """HTML을 완전히 순수 텍스트로 변환 (BeautifulSoup 사용)"""

    if not html_content or not html_content.strip():
        return '<p>내용이 없습니다.</p>'

    try:
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. script, style 태그 완전 제거
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()

        # 2. 이미지 완전 제거
        for img in soup.find_all('img'):
            img.decompose()

        # 3. 테이블을 텍스트로 변환
        for table in soup.find_all('table'):
            table_text = extract_table_text(table)
            if table_text:
                # 테이블을 텍스트 노드로 교체
                table.replace_with(BeautifulSoup(f'<p>{escape(table_text)}</p>', 'html.parser'))
            else:
                table.decompose()

        # 4. 모든 태그의 속성 제거 (href, src 등 모두 제거)
        for tag in soup.find_all(True):
            tag.attrs = {}

        # 5. a 태그는 텍스트만 남기고 제거
        for a in soup.find_all('a'):
            a.unwrap()

        # 6. 순수 텍스트 추출
        text = soup.get_text(separator='\n')

        # 7. 공백 정리
        text = re.sub(r'[ \t]+', ' ', text)  # 연속 공백
        text = re.sub(r'\n[ \t]+', '\n', text)  # 줄 시작 공백
        text = re.sub(r'[ \t]+\n', '\n', text)  # 줄 끝 공백
        text = re.sub(r'\n\n\n+', '\n\n', text)  # 과도한 줄바꿈
        text = text.strip()

        if not text:
            return '<p>내용이 없습니다.</p>'

        # 8. 문단 단위로 XHTML 생성 (속성 없이)
        paragraphs = text.split('\n\n')
        result = []

        for para in paragraphs:
            para = para.strip()
            if para:
                # 줄바꿈은 <br/>로
                lines = para.split('\n')
                para_text = '<br/>'.join(escape(line.strip()) for line in lines if line.strip())
                if para_text:
                    result.append(f'<p>{para_text}</p>')

        return '\n'.join(result) if result else f'<p>{escape(text)}</p>'

    except Exception as e:
        # 실패시 폴백
        print(f"⚠️ HTML 파싱 실패: {str(e)}")
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return f'<p>{escape(text)}</p>' if text else '<p>내용이 없습니다.</p>'


def create_epub(articles, output_path, options=None):
    """교보문고 호환 EPUB 2.0 생성 (EPUBCheck 통과)"""

    print(f"📚 EPUB 생성 시작: {len(articles)}개 기사")

    options = options or {}
    author = options.get('author_name', 'Unknown Author')
    title = options.get('title', f"{author} 기사 모음")
    publisher = options.get('publisher', 'Publisher')
    book_uuid = str(uuid.uuid4())

    temp_dir = tempfile.mkdtemp(prefix='epub_')

    try:
        # 디렉토리 구조
        os.makedirs(f"{temp_dir}/META-INF")
        os.makedirs(f"{temp_dir}/OEBPS")

        # 1. mimetype (압축 없이)
        with open(f"{temp_dir}/mimetype", "wb") as f:
            f.write(b"application/epub+zip")

        # 2. container.xml
        container = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''

        with open(f"{temp_dir}/META-INF/container.xml", "w", encoding="utf-8") as f:
            f.write(container)

        # 3. content.opf (EPUB 2.0)
        manifest_items = []
        spine_items = []

        for i in range(len(articles)):
            chapter_id = f"ch{i+1:04d}"
            manifest_items.append(
                f'        <item id="{chapter_id}" href="{chapter_id}.xhtml" media-type="application/xhtml+xml"/>'
            )
            spine_items.append(f'        <itemref idref="{chapter_id}"/>')

        opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{escape(title)}</dc:title>
        <dc:creator>{escape(author)}</dc:creator>
        <dc:identifier id="uid">urn:uuid:{book_uuid}</dc:identifier>
        <dc:language>ko</dc:language>
        <dc:publisher>{escape(publisher)}</dc:publisher>
        <dc:date>{datetime.now().strftime("%Y-%m-%d")}</dc:date>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{chr(10).join(manifest_items)}
    </manifest>
    <spine toc="ncx">
{chr(10).join(spine_items)}
    </spine>
</package>'''

        with open(f"{temp_dir}/OEBPS/content.opf", "w", encoding="utf-8") as f:
            f.write(opf)

        # 4. toc.ncx
        nav_points = []
        for i, article in enumerate(articles, 1):
            nav_title = escape(article.get("title", f"기사 {i}")[:100])
            nav_points.append(f'''        <navPoint id="nav{i}" playOrder="{i}">
            <navLabel>
                <text>{nav_title}</text>
            </navLabel>
            <content src="ch{i:04d}.xhtml"/>
        </navPoint>''')

        ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{book_uuid}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{escape(title)}</text>
    </docTitle>
    <navMap>
{chr(10).join(nav_points)}
    </navMap>
</ncx>'''

        with open(f"{temp_dir}/OEBPS/toc.ncx", "w", encoding="utf-8") as f:
            f.write(ncx)

        # 5. 각 챕터 (XHTML 1.1 엄격 준수)
        print(f"📄 {len(articles)}개 챕터 생성 중...")

        for i, article in enumerate(articles, 1):
            if i % 10 == 0 or i == len(articles):
                print(f"   {i}/{len(articles)} 처리 중...")

            # BeautifulSoup으로 완벽한 텍스트 추출
            content = html_to_pure_text(article.get('content', ''))

            article_title = escape(article.get('title', f'기사 {i}'))
            article_author = escape(article.get('author', ''))
            article_date = escape(article.get('date', '')[:10])

            # XHTML 1.1 (속성 없음, 최소한의 태그만)
            xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{article_title}</title>
</head>
<body>
<h1>{article_title}</h1>
<p>{article_author} - {article_date}</p>
{content}
</body>
</html>'''

            with open(f"{temp_dir}/OEBPS/ch{i:04d}.xhtml", "w", encoding="utf-8") as f:
                f.write(xhtml)

        # 6. EPUB 압축 (mimetype은 압축 없이)
        print("🗜️  EPUB 압축 중...")

        with zipfile.ZipFile(output_path, 'w') as epub:
            # mimetype 첫 번째, 압축 없이
            epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

            # 나머지 파일들 압축
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file != "mimetype":
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, temp_dir).replace('\\', '/')
                        epub.write(file_path, arc_path, compress_type=zipfile.ZIP_DEFLATED)

        # 검증
        file_size = os.path.getsize(output_path)
        print(f"\n✅ EPUB 생성 완료!")
        print(f"   파일: {output_path}")
        print(f"   크기: {file_size:,} bytes")
        print(f"   기사: {len(articles)}개")
        print(f"\n🔍 검증: https://www.pagina.gmbh/produkte/epub-checker/")

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """메인 함수"""

    if len(sys.argv) < 3:
        print("📖 사용법: python epub_generator.py input.json output.epub")
        print("\n예제:")
        print("  python epub_generator.py articles.json book.epub")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"❌ 입력 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)

    try:
        print(f"📂 입력 파일 읽기: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        articles = data.get('articles', [])
        if not articles:
            print("❌ 기사가 없습니다.")
            sys.exit(1)

        options = data.get('options', {})

        if create_epub(articles, output_file, options):
            print("\n✨ SUCCESS")
            sys.exit(0)
        else:
            sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
