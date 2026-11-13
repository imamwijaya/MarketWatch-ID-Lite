
const BACKEND_URL =
  process.env.FASTAPI_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const response = await fetch(
      `${BACKEND_URL}/api/observations`,
      {
        cache: "no-store",
        signal: AbortSignal.timeout(10000),
      }
    );

    if (!response.ok) {
      return Response.json(
        { error: "FastAPI returned an error" },
        { status: 502 }
      );
    }

    const data = await response.json();

    return Response.json(data, {
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return Response.json(
      { error: "Unable to connect to FastAPI" },
      { status: 502 }
    );
  }
}
