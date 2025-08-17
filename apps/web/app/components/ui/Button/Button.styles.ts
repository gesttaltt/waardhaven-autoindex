import { cva } from 'class-variance-authority';

export const buttonStyles = cva(
  'rounded-lg font-medium transition-all inline-flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        primary: 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 active:scale-[0.98]',
        secondary: 'bg-white/10 text-white hover:bg-white/20 border border-white/10',
        ghost: 'bg-transparent text-neutral-400 hover:text-white hover:bg-white/5',
        danger: 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30'
      },
      size: {
        sm: 'px-3 py-1.5 text-sm gap-1.5',
        md: 'px-4 py-2 text-base gap-2',
        lg: 'px-6 py-3 text-lg gap-2.5'
      },
      fullWidth: {
        true: 'w-full',
        false: 'w-auto'
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      fullWidth: false
    }
  }
);

export const loadingSpinnerStyles = 'animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full';