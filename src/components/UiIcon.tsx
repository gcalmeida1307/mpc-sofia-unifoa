import type { SVGProps } from "react"

export type IconName = "grid" | "chat" | "library" | "upload" | "network" | "link" | "pipeline" | "users" | "search" | "sun" | "moon" | "logout" | "arrow" | "chevron" | "menu" | "spark" | "file" | "shield"

const paths: Record<IconName, string> = {
  grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  chat: "M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4l-2 2V11.5a9.5 9.5 0 0 1 19 0Z M7 9h9 M7 13h6",
  library: "M4 4h4v16H4z M10 4h4v16h-4z M16 5l4-1 3 15-4 1z",
  upload: "M12 15V3 M7 8l5-5 5 5 M4 15v5h16v-5",
  network: "M9 12H5 M15 12h4 M12 9V5 M12 15v4 M9 9 5 5 M15 15l4 4 M9 15l-4 4 M15 9l4-4 M9 9h6v6H9z M2 2h3v3H2z M19 2h3v3h-3z M2 19h3v3H2z M19 19h3v3h-3z",
  link: "m10 13 4-4 M8 16l-1 1a4 4 0 0 1-6-6l4-4a4 4 0 0 1 6 0 M16 8l1-1a4 4 0 0 1 6 6l-4 4a4 4 0 0 1-6 0",
  pipeline: "M3 4h5v5H3z M16 15h5v5h-5z M8 6h8a3 3 0 0 1 0 6H8a3 3 0 0 0 0 6h8",
  users: "M16 21v-3a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v3 M13 6a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z M18 3a4 4 0 0 1 0 8 M22 21v-3a4 4 0 0 0-3-3.9",
  search: "M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z M15 15l6 6",
  sun: "M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l1 1 M18 18l1 1 M5 19l1-1 M18 6l1-1",
  moon: "M20.5 14a9 9 0 0 1-10.5-10.5A9 9 0 1 0 20.5 14Z",
  logout: "M9 4H3v16h6 M9 12h12 M17 8l4 4-4 4",
  arrow: "M4 12h16 M14 6l6 6-6 6",
  chevron: "m9 5 7 7-7 7",
  menu: "M4 6h16 M4 12h16 M4 18h16",
  spark: "m12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8Z",
  file: "M14 2H5v20h14V7Z M14 2v5h5 M8 12h8 M8 16h6",
  shield: "m12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6Z m-4 10 3 3 5-6",
}

export default function UiIcon({ name, ...props }: SVGProps<SVGSVGElement> & { name: IconName }) {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}><path d={paths[name]} /></svg>
}

