"""
YouTube Viral Video Search Script
Dùng YouTube Data API v3 để tìm video viral theo chủ đề.

Usage:
    python search_youtube.py "<chủ đề>" "<API_KEY>" [--max-results 10] [--order viewCount]

Output:
    In ra danh sách video dạng JSON với: title, views, likes, channel, url, description
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timedelta


def search_viral_videos(query: str, api_key: str, max_results: int = 10, order: str = "viewCount") -> list[dict]:
    """
    Tìm kiếm video viral trên YouTube theo chủ đề.

    Args:
        query: Từ khóa tìm kiếm
        api_key: YouTube Data API Key
        max_results: Số lượng kết quả tối đa (mặc định 10)
        order: Sắp xếp theo viewCount, relevance, date, rating

    Returns:
        Danh sách dict chứa thông tin video
    """

    # Bước 1: Tìm kiếm video IDs
    search_params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": order,
        "maxResults": max_results,
        "videoDuration": "short",          # Ưu tiên video ngắn (<4 phút)
        "relevanceLanguage": "vi",          # Ưu tiên nội dung tiếng Việt
        "publishedAfter": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "key": api_key
    })

    search_url = f"https://www.googleapis.com/youtube/v3/search?{search_params}"

    try:
        with urllib.request.urlopen(search_url) as resp:
            search_data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[ERROR] Không thể tìm kiếm: {e}", file=sys.stderr)
        return []

    if "items" not in search_data or not search_data["items"]:
        print("[INFO] Không tìm thấy kết quả nào.", file=sys.stderr)
        return []

    video_ids = [item["id"]["videoId"] for item in search_data["items"] if "videoId" in item.get("id", {})]

    if not video_ids:
        return []

    # Bước 2: Lấy thống kê chi tiết
    stats_params = urllib.parse.urlencode({
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": api_key
    })

    stats_url = f"https://www.googleapis.com/youtube/v3/videos?{stats_params}"

    try:
        with urllib.request.urlopen(stats_url) as resp:
            stats_data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[ERROR] Không thể lấy thống kê: {e}", file=sys.stderr)
        return []

    # Bước 3: Tổng hợp kết quả
    videos = []
    for item in stats_data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        # Tính engagement rate
        engagement = round((likes + comments) / views * 100, 2) if views > 0 else 0

        videos.append({
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", "")[:10],
            "description": snippet.get("description", "")[:300],
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate": engagement,
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "video_id": item["id"],
            "tags": snippet.get("tags", [])[:10],
        })

    # Sắp xếp theo views
    videos.sort(key=lambda x: x["views"], reverse=True)
    return videos


def format_number(n: int) -> str:
    """Format số lớn dễ đọc: 1234567 → 1.2M"""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def print_results(videos: list[dict], query: str) -> None:
    """In kết quả ra console dạng dễ đọc cho Claude."""

    print(f"\n{'='*60}")
    print(f"🔍 KẾT QUẢ TÌM KIẾM: '{query}'")
    print(f"📊 Tìm thấy {len(videos)} video viral")
    print(f"{'='*60}\n")

    for i, v in enumerate(videos, 1):
        print(f"## Video #{i}: {v['title']}")
        print(f"   📺 Kênh: {v['channel']}")
        print(f"   📅 Đăng: {v['published_at']}")
        print(f"   👁️  Views: {format_number(v['views'])}")
        print(f"   👍 Likes: {format_number(v['likes'])}")
        print(f"   💬 Comments: {format_number(v['comments'])}")
        print(f"   📈 Engagement: {v['engagement_rate']}%")
        print(f"   🔗 URL: {v['url']}")
        if v['description']:
            print(f"   📝 Mô tả: {v['description'][:150]}...")
        if v['tags']:
            print(f"   🏷️  Tags: {', '.join(v['tags'][:5])}")
        print()

    # Output JSON để Claude có thể parse
    print("\n--- JSON OUTPUT (cho Claude phân tích) ---")
    print(json.dumps(videos, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Tìm video viral YouTube theo chủ đề")
    parser.add_argument("query", help="Chủ đề tìm kiếm")
    parser.add_argument("api_key", help="YouTube Data API Key")
    parser.add_argument("--max-results", type=int, default=10, help="Số kết quả tối đa")
    parser.add_argument("--order", default="viewCount",
                       choices=["viewCount", "relevance", "date", "rating"],
                       help="Sắp xếp kết quả")
    parser.add_argument("--json-only", action="store_true", help="Chỉ in JSON, không in readable format")

    args = parser.parse_args()

    print(f"[INFO] Đang tìm kiếm video viral về '{args.query}'...", file=sys.stderr)

    videos = search_viral_videos(
        query=args.query,
        api_key=args.api_key,
        max_results=args.max_results,
        order=args.order
    )

    if not videos:
        print("[ERROR] Không tìm thấy video nào. Kiểm tra lại API key và kết nối mạng.", file=sys.stderr)
        sys.exit(1)

    if args.json_only:
        print(json.dumps(videos, ensure_ascii=False, indent=2))
    else:
        print_results(videos, args.query)


if __name__ == "__main__":
    main()
