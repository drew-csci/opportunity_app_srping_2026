import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChatWindow from "../ChatWindow";

describe("ChatWindow (unit)", () => {
  it("renders conversation header with organization name", () => {
    const conversation = {
      id: 1,
      other_user: { display_name: "Red Cross" },
      volunteer: { id: 123 },
    };
    const messages = [];

    render(
      <ChatWindow
        conversation={conversation}
        messages={messages}
        messageListEndRef={{ current: null }}
      />
    );

    expect(screen.getByText("Red Cross")).toBeInTheDocument();
  });

  it("renders messages correctly", () => {
    const conversation = {
      id: 1,
      other_user: { display_name: "Red Cross" },
      volunteer: { id: 123 },
    };
    const messages = [
      {
        id: 1,
        content: "Hello",
        timestamp: new Date().toISOString(),
        sender: { id: 123 },
      },
      {
        id: 2,
        content: "Hi there",
        timestamp: new Date().toISOString(),
        sender: { id: 456 },
      },
    ];

    render(
      <ChatWindow
        conversation={conversation}
        messages={messages}
        messageListEndRef={{ current: null }}
      />
    );

    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hi there")).toBeInTheDocument();
  });
});

