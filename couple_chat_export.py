#!/usr/bin/env python3
"""
微信单聊记录提取 + AI 预处理脚本
基于 chatlog 提取夫妻/情侣私聊数据，用于 AI 情感分析
"""

import json
import csv
import re
import os
from datetime import datetime
from pathlib import Path
import argparse


class CoupleChatExporter:
    """情侣/夫妻私聊数据导出工具"""
    
    def __init__(self, partner_name: str, data_dir: str = "~/.chatlog", output_dir: str = "./couple_chat"):
        self.partner_name = partner_name
        self.data_dir = Path(data_dir).expanduser()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 消息类型映射
        self.msg_types = {
            1: "text",      # 文字
            3: "image",     # 图片
            34: "voice",    # 语音
            43: "video",    # 视频
            47: "emoji",    # 表情
            49: "link",     # 链接/小程序
            50: "video_call", # 视频通话
            10000: "system",  # 系统消息
        }
    
    def extract_from_chatlog(self):
        """
        从 chatlog HTTP API 提取数据
        """
        print("=" * 60)
        print("💑 情侣聊天记录提取工具")
        print("=" * 60)
        
        print("\n【步骤1】启动 chatlog 服务")
        print("请先在终端执行以下命令：")
        print("  1. chatlog key          # 获取数据密钥")
        print("  2. chatlog decrypt      # 解密数据库")
        print("  3. chatlog server       # 启动 HTTP 服务")
        print("\n确认服务已启动后，按 Enter 继续...")
        input()
        
        import requests
        base_url = "http://127.0.0.1:5030"
        
        # 获取联系人列表（只找单聊）
        print("\n【步骤2】查找联系人...")
        try:
            response = requests.get(f"{base_url}/api/v1/contact", timeout=10)
            contacts = response.json()
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("请确认 chatlog server 已启动（端口 5030）")
            return None
        
        print(f"  找到 {len(contacts)} 个联系人")
        
        # 根据名字匹配伴侣
        partner = None
        candidates = []
        
        for contact in contacts:
            wxid = contact.get("wxid", "")
            # 跳过群聊（wxid 以 @chatroom 结尾的是群聊）
            if "@chatroom" in wxid:
                continue
                
            name = contact.get("remark") or contact.get("nickname") or wxid
            msg_count = contact.get("msg_count", 0)
            
            # 匹配伴侣名字
            if self.partner_name.lower() in name.lower() or \
               name.lower() in self.partner_name.lower():
                partner = {
                    "wxid": wxid,
                    "name": name,
                    "msg_count": msg_count
                }
                print(f"  ✅ 找到: {name} ({msg_count} 条消息)")
                break
            
            # 收集候选（消息数较多的私聊）
            if msg_count > 1000:
                candidates.append({
                    "wxid": wxid,
                    "name": name,
                    "msg_count": msg_count
                })
        
        if not partner:
            print(f"\n⚠️ 未找到 '{self.partner_name}'，请从以下候选中选择：")
            for i, c in enumerate(candidates[:10]):
                print(f"  {i+1}. {c['name']} ({c['msg_count']:,} 条)")
            
            choice = input("\n输入序号选择（或输入完整名字）: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(candidates):
                partner = candidates[int(choice)-1]
            else:
                # 重新搜索
                for c in candidates:
                    if choice.lower() in c['name'].lower():
                        partner = c
                        break
        
        if not partner:
            print("❌ 未找到联系人，请检查名字或手动选择")
            return None
        
        print(f"\n【步骤3】导出聊天记录: {partner['name']}")
        messages = self._fetch_all_messages(base_url, partner['wxid'])
        
        if not messages:
            print("❌ 未获取到消息")
            return None
        
        print(f"  ✅ 共 {len(messages):,} 条消息")
        
        return {
            "partner_name": partner['name'],
            "partner_wxid": partner['wxid'],
            "message_count": len(messages),
            "messages": messages
        }
    
    def _fetch_all_messages(self, base_url: str, wxid: str):
        """获取所有聊天记录（分页）"""
        import requests
        
        all_messages = []
        offset = 0
        batch_size = 1000
        
        while True:
            try:
                response = requests.get(
                    f"{base_url}/api/v1/chatlog",
                    params={
                        "talker": wxid,
                        "limit": batch_size,
                        "offset": offset,
                        "format": "json"
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    break
                
                messages = response.json()
                if not messages:
                    break
                
                all_messages.extend(messages)
                offset += batch_size
                
                # 显示进度
                if offset % 5000 == 0:
                    print(f"  已获取 {len(all_messages):,} 条...")
                
                if len(messages) < batch_size:
                    break
                    
            except Exception as e:
                print(f"  ⚠️ 获取中断: {e}")
                break
        
        return all_messages
    
    def convert_and_save(self, chat_data: dict):
        """
        转换并保存数据
        """
        print("\n【步骤4】数据处理与保存...")
        
        partner = chat_data['partner_name']
        messages = chat_data['messages']
        
        # 1. 保存完整 JSON
        json_path = self.output_dir / "chat_raw.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 原始数据: {json_path} ({len(json.dumps(chat_data)):,} bytes)")
        
        # 2. 导出 CSV 时间线
        csv_path = self.output_dir / "chat_timeline.csv"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "datetime", "date", "time", "year", "month", 
                "sender", "is_self", "msg_type", "content", "word_count"
            ])
            
            for msg in messages:
                time_str = msg.get("time", "")
                dt = self._parse_time(time_str)
                
                content = msg.get("content", "") or ""
                msg_type = self.msg_types.get(msg.get("type"), "other")
                is_self = msg.get("is_self", False)
                sender = "我" if is_self else partner
                
                writer.writerow([
                    time_str,
                    dt.strftime("%Y-%m-%d") if dt else "",
                    dt.strftime("H:%M:%S") if dt else "",
                    dt.year if dt else "",
                    dt.strftime("%Y-%m") if dt else "",
                    sender,
                    is_self,
                    msg_type,
                    content[:1000],  # 限制长度
                    len(content) if content else 0
                ])
        
        print(f"  ✅ 时间线 CSV: {csv_path}")
        
        # 3. 生成统计
        stats = self._generate_stats(messages, partner)
        stats_path = self.output_dir / "stats.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 统计报告: {stats_path}")
        
        # 4. 按时间切片（给 AI 分析用）
        self._slice_for_ai(messages, partner)
        
        return {
            "json": json_path,
            "csv": csv_path,
            "stats": stats_path
        }
    
    def _parse_time(self, time_str: str):
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            # 处理 ISO 格式
            time_str = time_str.replace("Z", "+00:00")
            return datetime.fromisoformat(time_str)
        except:
            try:
                return datetime.strptime(time_str[:19], "%Y-%m-%d %H:%M:%S")
            except:
                return None
    
    def _generate_stats(self, messages: list, partner: str):
        """生成统计信息"""
        print(f"\n  📊 生成统计...")
        
        # 基础统计
        total = len(messages)
        text_msgs = [m for m in messages if m.get("type") == 1]
        self_msgs = [m for m in messages if m.get("is_self")]
        partner_msgs = [m for m in messages if not m.get("is_self")]
        
        # 时间范围
        times = [self._parse_time(m.get("time", "")) for m in messages]
        times = [t for t in times if t]
        times.sort()
        
        # 年度统计
        yearly = {}
        monthly = {}
        hourly = {h: 0 for h in range(24)}
        
        for msg in messages:
            dt = self._parse_time(msg.get("time", ""))
            if not dt:
                continue
            
            year = dt.year
            month = dt.strftime("%Y-%m")
            hour = dt.hour
            
            yearly[year] = yearly.get(year, 0) + 1
            monthly[month] = monthly.get(month, 0) + 1
            hourly[hour] = hourly.get(hour, 0) + 1
        
        # 找出聊天高峰时段
        peak_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 最长对话
        contents = [m.get("content", "") for m in text_msgs if m.get("content")]
        avg_len = sum(len(c) for c in contents) / len(contents) if contents else 0
        
        return {
            "partner": partner,
            "total_messages": total,
            "text_messages": len(text_msgs),
            "my_messages": len(self_msgs),
            "partner_messages": len(partner_msgs),
            "date_range": {
                "start": times[0].strftime("%Y-%m-%d") if times else None,
                "end": times[-1].strftime("%Y-%m-%d") if times else None,
                "days": (times[-1] - times[0]).days if len(times) > 1 else 0
            },
            "yearly_messages": yearly,
            "monthly_messages": dict(sorted(monthly.items())[-12:]),  # 最近12个月
            "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
            "avg_message_length": round(avg_len, 2),
            "active_months": len(monthly)
        }
    
    def _slice_for_ai(self, messages: list, partner: str):
        """
        按时间段切片，方便 AI 分析
        """
        print(f"\n  ✂️  按时间段切片...")
        
        ai_dir = self.output_dir / "ai_analysis"
        ai_dir.mkdir(exist_ok=True)
        
        # 只取文字消息
        text_msgs = [m for m in messages if m.get("type") == 1 and m.get("content")]
        
        # 按年月分组
        monthly = {}
        for msg in text_msgs:
            dt = self._parse_time(msg.get("time", ""))
            if dt:
                key = dt.strftime("%Y-%m")
                if key not in monthly:
                    monthly[key] = []
                monthly[key].append(msg)
        
        # 导出每月对话
        exported_months = 0
        for month, msgs in sorted(monthly.items()):
            if len(msgs) < 10:  # 跳过消息太少的月份
                continue
            
            lines = []
            for msg in msgs:
                dt = self._parse_time(msg.get("time", ""))
                time_str = dt.strftime("%m-%d %H:%M") if dt else ""
                sender = "我" if msg.get("is_self") else partner
                content = msg.get("content", "").replace("\n", " ")
                lines.append(f"[{time_str}] {sender}: {content}")
            
            file_path = ai_dir / f"dialogue_{month}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"=== {month} 聊天记录 ===\n")
                f.write(f"共 {len(msgs)} 条文字消息\n\n")
                f.write("\n".join(lines))
            
            exported_months += 1
        
        print(f"  ✅ 导出 {exported_months} 个月度文件到: {ai_dir}")
        
        # 导出年度汇总
        yearly = {}
        for msg in text_msgs:
            dt = self._parse_time(msg.get("time", ""))
            if dt:
                year = dt.year
                if year not in yearly:
                    yearly[year] = []
                yearly[year].append(msg)
        
        for year, msgs in sorted(yearly.items()):
            # 每年选代表性对话（每个月抽一些）
            samples = msgs[::max(1, len(msgs)//500)]  # 抽样，每年最多500条
            
            lines = [f"=== {year} 年度聊天精选 ===", f"共 {len(msgs)} 条消息，抽样 {len(samples)} 条\n"]
            
            for msg in samples:
                dt = self._parse_time(msg.get("time", ""))
                time_str = dt.strftime("%m-%d") if dt else ""
                sender = "我" if msg.get("is_self") else partner
                content = msg.get("content", "").replace("\n", " ")[:150]
                lines.append(f"[{time_str}] {sender}: {content}")
            
            file_path = ai_dir / f"yearly_{year}_summary.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        
        print(f"  ✅ 导出 {len(yearly)} 个年度汇总文件")


def print_usage_examples(output_dir: Path, partner: str):
    """打印使用示例"""
    ai_dir = output_dir / "ai_analysis"
    
    print("\n" + "=" * 60)
    print("🎯 AI 分析使用指南")
    print("=" * 60)
    
    print(f"\n【数据文件位置】{output_dir.absolute()}")
    print(f"  - chat_raw.json       : 完整原始数据")
    print(f"  - chat_timeline.csv   : 时间线表格（Excel可打开）")
    print(f"  - stats.json          : 统计报告")
    print(f"  - ai_analysis/        : AI 分析专用切片")
    
    print("\n【单月度分析 Prompt】")
    print(f"  上传文件: ai_analysis/dialogue_2023-05.txt")
    print("""
请分析以下我和伴侣的聊天记录，输出：
1. 本月情感基调（积极/中性/消极，百分比）
2. 高频话题（Top 5）
3. 谁主动发起对话更多
4. 最暖心的3个瞬间
5. 如果有矛盾，简要说明
  """)
    
    print("\n【年度趋势分析 Prompt】")
    print(f"  上传文件: ai_analysis/yearly_2023_summary.txt")
    print("""
请分析我们2023年的聊天趋势：
1. 这一年的关系发展曲线
2. 聊天频率变化及可能原因
3. 共同关注的话题演变
4. 给我们的年度关键词
  """)
    
    print("\n【数据可视化建议】")
    print("  用 chat_timeline.csv 在 Excel/Numbers 中制作：")
    print("  - 折线图: 每月消息量趋势")
    print("  - 柱状图: 每天24小时聊天分布")
    print("  - 词云: 高频关键词")
    
    print("\n⚠️ 安全提醒:")
    print("  1. 分析完成后删除 ~/.chatlog/ 下的解密文件")
    print("  2. 导出的文本文件请妥善保管")
    print("  3. 上传到 AI 时注意隐私，建议用本地模型")


def main():
    parser = argparse.ArgumentParser(
        description="情侣/夫妻微信单聊记录提取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python couple_chat_export.py --partner "老婆" --output ./my_love
  python couple_chat_export.py --partner "宝贝" --output ./7years_chat
        """
    )
    parser.add_argument(
        "--partner", "-p",
        required=True,
        help="伴侣在微信中的备注名或昵称（如：老婆、宝贝、亲爱的）"
    )
    parser.add_argument(
        "--output", "-o",
        default="./couple_chat",
        help="输出目录（默认: ./couple_chat）"
    )
    parser.add_argument(
        "--data-dir",
        default="~/.chatlog",
        help="chatlog 数据目录（默认: ~/.chatlog）"
    )
    
    args = parser.parse_args()
    
    # 创建导出器
    exporter = CoupleChatExporter(
        partner_name=args.partner,
        data_dir=args.data_dir,
        output_dir=args.output
    )
    
    # 执行提取
    chat_data = exporter.extract_from_chatlog()
    
    if not chat_data:
        print("\n❌ 提取失败，请检查错误信息后重试")
        return
    
    # 转换保存
    files = exporter.convert_and_save(chat_data)
    
    # 打印使用指南
    print_usage_examples(Path(args.output), args.partner)
    
    print("\n" + "=" * 60)
    print("✅ 全部完成！明天早上可以开始 AI 分析了 🌅")
    print("=" * 60)


if __name__ == "__main__":
    main()
