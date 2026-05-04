import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ConversationList from "../ConversationList";

describe("ConversationList (unit)", () => {
  it("renders conversations correctly and allows selection", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    const conversations = [
      { id: 1, volunteer_name: "Alice", organization_name: "Red Cross" },
      { id: 2, volunteer_name: "Alice", organization_name: "Food Bank" },
    ];

    render(<ConversationList conversations={conversations} activeId={1} onSelect={onSelect} />);

    expect(screen.getByText("Red Cross")).toBeInTheDocument();
    expect(screen.getByText("Food Bank")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Food Bank/i }));
    expect(onSelect).toHaveBeenCalledWith(2);
  });
});

