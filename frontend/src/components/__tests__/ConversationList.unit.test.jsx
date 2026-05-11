import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ConversationList from "../ConversationList";

describe("ConversationList (unit)", () => {
  it("renders conversations correctly and allows selection", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    const conversations = [
      {
        id: 1,
        other_user: { display_name: "Red Cross" },
        last_message: "Hello",
        last_message_at: new Date().toISOString(),
      },
      {
        id: 2,
        other_user: { display_name: "Food Bank" },
        last_message: "Hi there",
        last_message_at: new Date().toISOString(),
      },
    ];

    render(
      <ConversationList
        conversations={conversations}
        selectedConversation={null}
        onConversationSelect={onSelect}
        onCreateConversation={vi.fn()}
      />
    );

    expect(screen.getByText("Red Cross")).toBeInTheDocument();
    expect(screen.getByText("Food Bank")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Food Bank/i }));
    expect(onSelect).toHaveBeenCalledWith(conversations[1]);
  });
});

