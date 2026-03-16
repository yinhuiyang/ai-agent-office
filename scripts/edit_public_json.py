import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"JSON 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            # 空文件时返回 None，由调用方根据操作意图决定初始化为 {} 或 []
            return None
        return json.loads(content)


def save_json(path: Path, data: Any) -> None:
    # 统一用 UTF-8、带缩进的格式保存，方便在项目里直接查看
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")


def parse_set_items(items: List[str]) -> Dict[str, Any]:
    """
    将 --set key=value 解析为字典。
    value 默认按字符串处理，如果是合法 JSON（例如 1, true, {"a":1}）则按 JSON 解析。
    """
    result: Dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--set 需要 key=value 格式，当前: {item}")
        key, raw_value = item.split("=", 1)
        raw_value = raw_value.strip()
        # 尝试按 JSON 解析（支持数字、布尔、对象等），失败则用字符串
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            value = raw_value
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="修改项目 public 目录下的 JSON 文件的小工具"
    )
    parser.add_argument(
        "--filename",
        required=True,
        help="要修改的 JSON 文件名，例如: rule.json / skill.json / state.json",
    )
    parser.add_argument(
        "--set",
        dest="set_items",
        action="append",
        default=[],
        help="设置字段，格式为 key=value，可多次使用；value 支持 JSON，例如 progress=50 或 progress=0.5 或 data='{\"a\":1}'",
    )
    parser.add_argument(
        "--append",
        dest="append_items",
        action="append",
        default=[],
        help="向数组 JSON 追加元素，内容为完整 JSON 字符串，可多次使用，例如: --append '{\"name\":\"xxx\"}'",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="当目标 JSON 文件不存在时自动创建（默认不创建）",
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    public_dir = project_root / "public"
    json_path = public_dir / args.filename

    if not json_path.exists():
        if not args.create:
            raise FileNotFoundError(f"JSON 文件不存在: {json_path}（可加 --create 自动创建）")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text("", encoding="utf-8")

    data = load_json(json_path)
    if data is None:
        # 空文件时，根据用户操作自动初始化根类型
        data = [] if args.append_items and not args.set_items else {}

    # 处理 --set
    if args.set_items:
        if not isinstance(data, dict):
            raise TypeError(
                f"{args.filename} 的根类型不是对象，不能使用 --set（当前类型: {type(data).__name__})"
            )
        updates = parse_set_items(args.set_items)
        data.update(updates)

    # 处理 --append
    if args.append_items:
        if not isinstance(data, list):
            raise TypeError(
                f"{args.filename} 的根类型不是数组，不能使用 --append（当前类型: {type(data).__name__})"
            )
        for item in args.append_items:
            try:
                value = json.loads(item)
            except json.JSONDecodeError as e:
                raise ValueError(f"--append 需要合法 JSON，当前: {item}") from e
            data.append(value)

    save_json(json_path, data)

    print(f"已更新: {json_path}")


if __name__ == "__main__":
    main()

