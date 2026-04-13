"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function App() {
  const router = useRouter();

  useEffect(() => {
    router.push("/homepage/");
  }, [router]);

  return null; // or a loading spinner if you want
}
