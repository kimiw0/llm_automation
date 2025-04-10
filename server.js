import express from "express";
import multer from "multer";
import fs from "fs";
import cors from "cors";

const app = express();
const port = process.env.PORT || 3000;
const upload = multer({ dest: "uploads/" });

app.use(cors());

app.post("/api", upload.single("file"), async (req, res) => {
  const question = req.body.question || "";

  // Simple logic for demo
  let answer = "default answer";
  if (question.includes("answer column")) answer = "1234567890";

  // Cleanup
  if (req.file) {
    fs.unlinkSync(req.file.path);
  }

  res.json({ answer });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
