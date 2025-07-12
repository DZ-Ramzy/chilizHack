import { cn } from "../lib/utils";

const reviews = [
  {
    name: "Marco",
    username: "@marco_juve",
    body: "Got VIP access to Juventus training and $CHZ rewards. Amazing!",
    img: "https://avatar.vercel.sh/marco_juve",
  },
  {
    name: "Sophie",
    username: "@psg_sophie",
    body: "Love voting on PSG decisions with my fan tokens! 🔥",
    img: "https://avatar.vercel.sh/psg_sophie",
  },
  {
    name: "Carlos",
    username: "@barca_carlos",
    body: "Met Lewandowski through Barça fan quests. Dream come true!",
    img: "https://avatar.vercel.sh/barca_carlos",
  },
  {
    name: "Emma",
    username: "@arsenal_emma",
    body: "Exclusive Arsenal merch from team challenges. Worth it! ⚽️",
    img: "https://avatar.vercel.sh/arsenal_emma",
  },
  {
    name: "Luca",
    username: "@inter_luca",
    body: "Match predictions for Inter tokens make games exciting! 🏆",
    img: "https://avatar.vercel.sh/inter_luca",
  },
  {
    name: "Alex",
    username: "@city_alex",
    body: "Man City stadium tour and player meet-ups. Best rewards ever!",
    img: "https://avatar.vercel.sh/city_alex",
  },
];

const ReviewCard = ({
  img,
  name,
  username,
  body,
}: {
  img: string;
  name: string;
  username: string;
  body: string;
}) => {
  return (
    <figure
      className={cn(
        "relative h-full w-64 cursor-pointer overflow-hidden rounded-xl border p-4",
        "border-gray-950/[.1] bg-gray-950/[.01] hover:bg-gray-950/[.05]",
        "dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]",
      )}
    >
      <div className="flex flex-row items-center gap-2">
        <img className="rounded-full" width="32" height="32" alt="" src={img} />
        <div className="flex flex-col">
          <figcaption className="text-sm font-medium dark:text-white">
            {name}
          </figcaption>
          <p className="text-xs font-medium dark:text-white/40">{username}</p>
        </div>
      </div>
      <blockquote className="mt-2 text-sm">{body}</blockquote>
    </figure>
  );
};

export default function Reviews() {
  return (
    <div className="relative w-full overflow-hidden">
      <style jsx>{`
        .scroll {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          width: max-content;
          animation: scroll 30s linear infinite;
        }
        
        .scroll-reverse {
          animation-direction: reverse;
        }

        .scroll:hover {
          animation-play-state: paused;
        }

        @keyframes scroll {
          from {
            transform: translateX(0);
          }
          to {
            transform: translateX(calc(-50%));
          }
        }

        .container {
          display: flex;
          gap: 2rem;
          flex-direction: column;
          padding: 2rem 0;
        }

        .track {
          display: flex;
          width: 100%;
          overflow: hidden;
        }
      `}</style>

      <div className="container">
        <div className="track">
          <div className="scroll">
            {[...reviews, ...reviews].map((review, i) => (
              <ReviewCard key={`${review.username}-${i}`} {...review} />
            ))}
          </div>
        </div>

        <div className="track">
          <div className="scroll scroll-reverse">
            {[...reviews, ...reviews].map((review, i) => (
              <ReviewCard key={`${review.username}-${i}`} {...review} />
            ))}
          </div>
        </div>
      </div>

      <div className="pointer-events-none absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-background to-transparent"></div>
      <div className="pointer-events-none absolute inset-y-0 right-0 w-1/3 bg-gradient-to-l from-background to-transparent"></div>
    </div>
  );
}
