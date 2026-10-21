"""공개 API로 15분 데모 채용 건과 지원자 초대 링크를 만든다.

    uv run --project services/api python scripts/make_session.py --minutes 15
"""

import argparse

import httpx

from seed import admin_token, create_position


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--email", default="admin@dayzero.example")
    parser.add_argument("--password", default="dayzero-seed")
    parser.add_argument("--company", default="데모 회사")
    parser.add_argument("--position", default="서비스기획 신입")
    parser.add_argument("--minutes", type=int, choices=(15, 60), default=15)
    parser.add_argument("--name", default="김지원")
    parser.add_argument("--candidate-email", default="candidate@example.com")
    args = parser.parse_args()
    with httpx.Client(base_url=args.api, timeout=30) as client:
        token = admin_token(client, args.email, args.password, args.company)
        position = create_position(client, token, args.position, args.minutes, "debate")
        response = client.post(
            f"/admin/positions/{position['id']}/invites",
            json={"alias": args.name, "email": args.candidate_email},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        print(response.json()["invite_url"])


if __name__ == "__main__":
    main()
