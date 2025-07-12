import { cn } from "../../lib/utils";
import { ComponentPropsWithoutRef } from "react";

interface MarqueeProps extends ComponentPropsWithoutRef<"div"> {
  className?: string;
  reverse?: boolean;
  pauseOnHover?: boolean;
  children: React.ReactNode;
}

export function Marquee({
  className,
  reverse = false,
  pauseOnHover = false,
  children,
  ...props
}: MarqueeProps) {
  return (
    <div
      {...props}
      className={cn(
        "group relative w-full overflow-x-hidden",
        className
      )}
    >
      <div
        className={cn(
          "flex w-fit animate-marquee",
          {
            "[animation-direction:reverse]": reverse,
            "group-hover:[animation-play-state:paused]": pauseOnHover,
          }
        )}
      >
        <div className="flex">
          {children}
        </div>
        <div className="flex">
          {children}
        </div>
      </div>
    </div>
  );
}
