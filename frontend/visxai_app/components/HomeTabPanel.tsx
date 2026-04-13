"use client";
import { useRouter } from "next/navigation";
export const HomeTabPanel = () => {
  const router = useRouter();
  return (

    <div className="flex items-center justify-between mb-12">
      <div className="flex items-center space-x-2">
          <img src="/icon/logo.png" alt="Logo" width={90} height={90} />
          <h1 className="text-4xl font-bold text-blue-700">VisX.AI</h1>
      </div>
      <nav className="flex space-x-70">
          <a href="#" onClick={() => router.push("/homepage")} className="text-2xl text-gray-800 hover:text-blue-600">Home</a>
          <a href="#" className=" text-2xl text-gray-800 hover:text-blue-600">Introduction</a>
          <a href="#" className="text-2xl text-gray-800 hover:text-blue-600">Who we are</a>
      </nav>
      <button className="text-2xl bg-green-700 text-white px-4 py-2 rounded">Settings</button>
    </div>
  );
};
export default HomeTabPanel;