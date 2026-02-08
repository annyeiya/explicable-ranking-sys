import { useState } from "react";
import { Card, Button } from "react-bootstrap";
import "./ExpandableCard.css";

export const ExpandableCard = ({ item, isSelected, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card
      className="mb-2"
      onClick={onSelect}
      style={{
        cursor: "pointer",
        border: isSelected ? "2px solid var(--theme-color)" : "1px solid #ccc",
      }}
    >
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start">
          <div className="flex-grow-1">
            <Card.Title>{item.org}</Card.Title>
            <Card.Text>Total Score: {item.totalScore}</Card.Text>
          </div>
          <Button 
            variant="outline-secondary"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="expand-btn"
          >
            {isExpanded ? '▲' : '▼'}
          </Button>
        </div>

        {isExpanded && (
          <div className="mt-3">
            {item.matchedPhrases.map((mp, idx) => (
              <div key={idx}>
                <strong>Фраза:</strong> {mp.textPhrase}
                <br />
                <strong>Функция:</strong> {mp.function}
                <br />
                <strong>similarity:</strong> {mp.similarity}
                <hr />
              </div>
            ))}
          </div>
        )}
      </Card.Body>
    </Card>
  );
};