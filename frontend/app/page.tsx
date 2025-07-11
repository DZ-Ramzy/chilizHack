import Image from "next/image";
import ScrollingBanner from "../components/ScrollingBanner";
import Missions from "../components/Missions";

export default function Home() {
  return (
    <>
      {/*<video
        autoPlay
        loop
        muted
        playsInline
        className="fixed top-0 left-0 w-full h-full object-cover -z-10"
      >
        <source src="/bg.mp4" type="video/mp4" />
      </video>*/}
      <ScrollingBanner />
    </>
  );
}
