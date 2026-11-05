import { MantineProvider } from "@mantine/core";
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import FocusReading from "./FocusReading";

it("shows record provenance and keeps excluded methods separate", () => {
  const open = vi.fn();
  const hit = {
    path: "crypto/rsa.md",
    title: "共模",
    category: "crypto",
    score: 1,
    snippet: "",
    section: "解题步骤",
    focus_basis: [
      { field: "facts", label: "近期已确认事实", text: "同一个 n" },
    ],
  };
  render(
    <MantineProvider>
      <FocusReading
        onOpenDoc={open}
        focus={{
          workspace_id: "ws1",
          title: "题目 A",
          basis: hit.focus_basis,
          hits: [hit],
          excluded: [{ ...hit, title: "广播", path: "crypto/broadcast.md" }],
        }}
      />
    </MantineProvider>,
  );
  fireEvent.click(screen.getByRole("button", { name: "共模" }));
  expect(open).toHaveBeenCalledWith("crypto/rsa.md", "共模");
  expect(screen.getByText("根据：近期已确认事实「同一个 n」")).toBeTruthy();
  fireEvent.click(screen.getByText("条件不符的路径（1）"));
  expect(screen.getByRole("button", { name: "广播" })).toBeTruthy();
});
