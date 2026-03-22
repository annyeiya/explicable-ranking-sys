import { useState } from "react";
import { Button, OverlayTrigger, Tooltip, Form } from "react-bootstrap";
import mammoth from "mammoth";
import { sendText } from "../api/baseApi.js";
import "./BasePage.css";
import { ExpandableCard } from "../components/ExpandableCard.jsx"

export default function BasePage() {
  const [inputText, setInputText] = useState("");
  const [responseData, setResponseData] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isLocked, setIsLocked] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  async function handleSubmit(e) {
    if (!inputText.trim()) {
      setError("Введите текст перед отправкой");
      return;
    }

    setLoading(true);
    setError(null);
    setIsLocked(true);
    setHasSearched(true); 

    try {
      const answer = await sendText(inputText);
      setResponseData(answer || []);
    } catch (err) {
      console.error(err);
      setError("Не удалось получить ответ от сервера.");
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setInputText("");
    setResponseData([]);
    setError(null);
    setIsLocked(false);
    setSelectedOrg(null);
    setHasSearched(false);
  }

  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const fileType = file.name.split(".").pop().toLowerCase();

    try {
      if (fileType === "txt") {
        const text = await file.text();
        setInputText(text);
      }

      else if (fileType === "docx") {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        setInputText(result.value);
      }

      else {
        alert("Поддерживаются только .txt и .docx");
      }

    } catch (err) {
      console.error(err);
      alert("Ошибка при чтении файла");
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave() {
    setIsDragging(false);
  }

  async function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (!file) return;

    const fileType = file.name.split(".").pop().toLowerCase();

    try {
      if (fileType === "txt") {
        const text = await file.text();
        setInputText(text);
      } 
      else if (fileType === "docx") {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        setInputText(result.value);
      } 
      else {
        alert("Поддерживаются только .txt и .docx");
      }
    } catch (err) {
      console.error(err);
      alert("Ошибка при чтении файла");
    }
  }

  // Нормализация для поиска
  const normalize = (str) => str.toLowerCase().replace(/\s+/g, ' ').trim();

  // Собираем все совпадения с позициями
  const allMatches = [];

  responseData.forEach(item => {
    item.matchedPhrases.forEach(mp => {
      const normalizedInput = normalize(inputText);
      const normalizedPhrase = normalize(mp.textPhrase);
      
      let startPos = 0;
      while (true) {
        const start = normalizedInput.indexOf(normalizedPhrase, startPos);
        if (start === -1) break;
        
        allMatches.push({
          start,
          end: start + normalizedPhrase.length,
          normalizedPhrase,
          org: item.org,
          function: mp.function,
          similarity: mp.similarity,
        });
        
        startPos = start + 1;
      }
    });
  });

  // Группируем по позиции в тексте
  const groupedByPosition = [];
  allMatches.sort((a, b) => a.start - b.start);

  allMatches.forEach(match => {
    const existing = groupedByPosition.find(g => 
      !(match.end <= g.start || match.start >= g.end)
    );
    
    if (existing) {
      // Расширяем диапазон 
      existing.start = Math.min(existing.start, match.start);
      existing.end = Math.max(existing.end, match.end);
      existing.items.push({
        org: match.org,
        function: match.function,
        similarity: match.similarity,
      });
    } else {
      groupedByPosition.push({
        start: match.start,
        end: match.end,
        items: [{
          org: match.org,
          function: match.function,
          similarity: match.similarity,
        }],
      });
    }
  });

  // Рендерим
  const segments = [];
  let lastIndex = 0;

  groupedByPosition.forEach((group, i) => {
    if (group.start > lastIndex) {
      segments.push(
        <span key={`pre-${i}`}>{inputText.slice(lastIndex, group.start)}</span>
      );
    }

    // Определяем подсветку: есть ли среди items нужный org
    const belongsToSelected = selectedOrg && 
      group.items.some(p => p.org === selectedOrg);
    
    const shouldHighlight = belongsToSelected;

    // Фильтруем данные для tooltip
    const filteredData = selectedOrg
      ? group.items.filter(p => p.org === selectedOrg)
      : group.items;

    // Берём оригинальный текст из inputText 
    const originalText = inputText.slice(group.start, group.end);

    segments.push(
      <span key={`match-${i}`}>
        {shouldHighlight ? (
          <OverlayTrigger
            placement="bottom"
            overlay={
              <Tooltip id={`tooltip-${i}`}>
                {filteredData.map((d, j) => (
                  <div key={j}>
                    <b>{d.function}</b> — ({d.similarity})
                    <hr />
                  </div>
                ))}
              </Tooltip>
            }
          >
            <mark>{originalText}</mark>
          </OverlayTrigger>
        ) : (
          originalText
        )}
        {" "}
      </span>
    );

    lastIndex = group.end;
  });

  // Остаток
  if (lastIndex < inputText.length) {
    segments.push(<span key="end">{inputText.slice(lastIndex)}</span>);
  }

  const renderedText = segments;




  return (
    <>
      {/* Левая колонка: ввод */}
      <div className={`input-column ${isDragging ? "drag-active" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >

        {isLocked ? (
          <div className="read-only-box">
            {renderedText}
          </div>
        ) : (
        <Form.Control
          as="textarea"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="input-textarea"
          placeholder="Введите текст запроса..."
        />
        )}

        <br></br>

        {/* Кнопка загрузки файла */}
        {!isLocked && (
          <>
            <Button
              className="btn-load"
              onClick={() => document.getElementById("fileInput").click()}
            >
              Загрузить файл (.txt, .docx)
            </Button>

            <input
              id="fileInput"
              type="file"
              accept=".txt,.docx"
              style={{ display: "none" }}
              onChange={handleFileUpload}
            />
          </>
        )}

      </div>

      {/* Правая колонка: вывод + кнопки */}
      <div className="output-column">
        <div className="output-content">
          <h5>Топ органов:</h5>
          {error && (
            <div className="text-danger">
              {error}
            </div>
          )}

          {loading && (
            <div className="text-muted">
              Поиск органов...
            </div>
          )}

          {!loading && !error && !hasSearched && (
            <div className="text-muted">
              Здесь появится результат анализа
            </div>
          )}

          {!loading && !error && hasSearched && responseData.length === 0 && (
            <div className="text-warning">
              Упс... по данному тексту совпадений не найдено
            </div>
          )}
          
        {responseData.map((item, index) => (
            <ExpandableCard
              key={index}
              item={item}
              isSelected={selectedOrg === item.org}
              onSelect={() => setSelectedOrg(item.org)}
            />
          ))}
        </div>

        <div className="buttons-row">
          <Button 
            className="btn-custom"
            onClick={handleSubmit} 
            disabled={loading}
          >
            {loading ? "Обработка..." : "Обработать"}
          </Button>
          <Button variant="secondary" onClick={handleClear}>
            Очистить
          </Button>
        </div>
      </div>
    </>
  );
}
