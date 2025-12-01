#!/usr/bin/env python3
"""
─────────────────────────────────────────────
 dynamic_inventory.py — K3s 동적 인벤토리
─────────────────────────────────────────────
- kubectl을 사용해 현재 K3s 클러스터의 노드 목록을 조회하고,
  Ansible이 이해할 수 있는 JSON 인벤토리 형식으로 반환합니다.
─────────────────────────────────────────────
"""

import json
import subprocess
import sys


def get_k3s_nodes():
    """kubectl 명령을 통해 노드 정보를 JSON으로 가져옵니다."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "nodes", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        # 실패 시 빈 인벤토리 반환
        return {"items": []}


def generate_inventory():
    """K3s 노드 정보를 기반으로 Ansible 인벤토리(JSON) 생성"""
    data = get_k3s_nodes()

    # 기본 인벤토리 구조
    inventory = {
        "k3s_master": {"hosts": {}},
        "k3s_nodes": {"hosts": {}},
        "_meta": {"hostvars": {}}
    }

    for node in data["items"]:
        name = node["metadata"]["name"]
        ip = None
        role = "k3s_nodes"  # 기본은 worker

        # 내부 IP 추출
        for addr in node["status"]["addresses"]:
            if addr["type"] == "InternalIP":
                ip = addr["address"]
                break

        # 라벨을 보고 master 판별
        labels = node["metadata"].get("labels", {})
        if ("node-role.kubernetes.io/master" in labels or
            "node-role.kubernetes.io/control-plane" in labels):
            role = "k3s_master"

        # 인벤토리에 추가
        inventory[role]["hosts"][name] = {"ansible_host": ip}
        inventory["_meta"]["hostvars"][name] = {"ansible_user": "root"}

    return inventory


def main():
    """명령행 인자 처리 (Ansible 요구 형식 준수)"""
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(generate_inventory(), indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        # 단일 호스트 조회용 (필수 placeholder)
        print(json.dumps({}))
    else:
        print("Usage: dynamic_inventory.py --list or --host <hostname>")
        sys.exit(1)


if __name__ == "__main__":
    main()

