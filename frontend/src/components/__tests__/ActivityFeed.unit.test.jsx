import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ActivityFeed from "../ActivityFeed";

describe("ActivityFeed (unit)", () => {
  it("renders activity items correctly when feed data exists", async () => {
    const items = [
      {
        id: 1,
        volunteer_name: "Alice",
        organization_name: "Helping Hands",
        title: "Packed meals",
        created_at: "2026-03-01T10:00:00Z",
      },
      {
        id: 2,
        volunteer_name: "Bob",
        organization_name: "Food Bank",
        title: "Delivered supplies",
        created_at: "2026-03-02T12:00:00Z",
      },
    ];

    const fetchActivityFeed = async () => items;

    render(
      <ActivityFeed
        fetchActivityFeed={fetchActivityFeed}
        fallbackItems={[]}
        apiBase="http://example.test"
      />
    );

    expect(await screen.findByText("Peer Activity Feed")).toBeInTheDocument();
    expect(await screen.findByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Helping Hands")).toBeInTheDocument();
    expect(screen.getByText("Packed meals")).toBeInTheDocument();

    expect(await screen.findByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Food Bank")).toBeInTheDocument();
    expect(screen.getByText("Delivered supplies")).toBeInTheDocument();

    expect(screen.queryByText("No recent activity available")).not.toBeInTheDocument();
  });

  it('renders "No recent activity available" when feed data is empty', async () => {
    const fetchActivityFeed = async () => [];

    render(
      <ActivityFeed
        fetchActivityFeed={fetchActivityFeed}
        fallbackItems={[]}
        apiBase="http://example.test"
      />
    );

    expect(await screen.findByText("Peer Activity Feed")).toBeInTheDocument();
    expect(await screen.findByText("No recent activity available")).toBeInTheDocument();
  });
});

