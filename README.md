# Campus AI Cloud

## 概要

Campus AI Cloudは教育機関向け生成AIクラウドサービスです。

学生・教員が教材PDFを利用しながら質問できるRAGシステムを提供します。

---

## 使用技術

- Docker Desktop
- Docker Compose
- Open WebUI
- Granite 4 3B
- Kubernetes（予定）
- Oracle Cloud（予定）

---

## 主な機能

- AIチャット
- 教材PDF検索（RAG）
- 学校専用AI
- 教材を利用した回答

---

## 起動方法

```bash
docker compose up -d
```

ブラウザ

```
http://localhost:3000
```

---

## システム構成

```
ブラウザ
    ↓
Open WebUI
    ↓
Granite4
    ↓
教材PDF
```
