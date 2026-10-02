import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

async function proxy(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const backend = process.env.BACKEND_API_URL?.replace(/\/$/, "");

  if (!backend) {
    return NextResponse.json(
      { detail: "BACKEND_API_URL is not configured" },
      { status: 500 }
    );
  }

  const { path } = await params;
  const target = `${backend}/${path.join("/")}${request.nextUrl.search}`;

  try {
    const response = await fetch(target, {
      method: request.method,
      headers: {
        accept: request.headers.get("accept") || "application/json",
        "content-type":
          request.headers.get("content-type") || "application/json",
      },
      cache: "no-store",
    });

    const body = await response.text();

    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type":
          response.headers.get("content-type") || "application/json",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        detail: "Backend connection failed",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 502 }
    );
  }
}

export const GET = proxy;
