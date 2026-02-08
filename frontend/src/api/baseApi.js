export async function sendText(text) {
    const res = await fetch("/api/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
    });

    if (!res.ok) {
        throw new Error(`Ошибка: ${res.status}`);
    }

    const data = await res.json();
    return Array.isArray(data) ? data : [];
}