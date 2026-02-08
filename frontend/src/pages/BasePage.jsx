import { useState } from "react";
import { Button, OverlayTrigger, Tooltip, Form } from "react-bootstrap";
import { sendText } from "../api/baseApi.js";
import "./BasePage.css";
import { ExpandableCard } from "../components/ExpandableCard.jsx"

export default function BasePage() {
  const [inputText, setInputText] = useState("");
  const [responseData, setResponseData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isLocked, setIsLocked] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState(null);

  async function handleSubmit(e) {
    if (!inputText.trim()) {
      setError("Введите текст перед отправкой");
      return;
    }

    setLoading(true);
    setError(null);
    setIsLocked(true);

    try {
      const answer = await sendText(inputText);
      setResponseData(answer);
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
  }

  // Строим карту фраз
  const phraseMap = {};
  responseData.forEach((item) => {
    item.matchedPhrases.forEach((mp) => {
      const phrase = mp.textPhrase.trim();
      if (!phraseMap[phrase]) phraseMap[phrase] = [];
      phraseMap[phrase].push({
        function: mp.function,
        similarity: mp.similarity,
        org: item.org,
      });
    });
  });

  // Подсветка текста
  const renderedText = inputText.split(/(?<=\.)\s*/).map((sentence, i) => {
    const phraseData = phraseMap[sentence.trim()];
    if (!phraseData) return <span key={i}>{sentence} </span>;

    const belongsToSelected =
      selectedOrg &&
      phraseData.some((p) => p.org === selectedOrg);

    const shouldHighlight = belongsToSelected;

    const filteredData = selectedOrg
        ? phraseData.filter((p) => p.org === selectedOrg)
        : phraseData;
    
    const content = (
      <span key={i}>
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
            <mark>
              {sentence}
            </mark>
          </OverlayTrigger>
        ) : (
          sentence
        )}
        {" "}
      </span>
    );

    return content;
  });

  return (
    <>
      {/* Левая колонка: ввод */}
      <div className="input-column">
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
      </div>

      {/* Правая колонка: вывод + кнопки */}
      <div className="output-column">
        <div className="output-content">
          <h5>Топ органов:</h5>
          {error && <div className="text-danger">{error}</div>}
          {!error && !responseData && (
            <div className="text-muted">Здесь появится ответ</div>
          )}
          {/* //TODO if answer is empty*/}

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
            {loading ? "Отправка..." : "Отправить"}
          </Button>
          <Button variant="secondary" onClick={handleClear}>
            Очистить
          </Button>
        </div>
      </div>
    </>
  );
}
