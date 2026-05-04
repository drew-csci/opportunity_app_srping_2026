import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "../App";

describe("ActivityFeed (integration)", () => {
  it("renders the full ActivityFeed/page with mock fallback when backend is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => {
      throw new Error("network down");
    }));

    render(<App />);

    expect(await screen.findByText("Peer Activity Feed")).toBeInTheDocument();
    expect(await screen.findByLabelText("activity-feed")).toBeInTheDocument();

    // From built-in mock fallback data
    expect(await screen.findByText("Tin Tin Do")).toBeInTheDocument();
    expect(screen.getByText("Red Cross")).toBeInTheDocument();
    expect(screen.getByText("Tutored students")).toBeInTheDocument();
  });
});

