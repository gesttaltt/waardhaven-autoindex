import { cva } from 'class-variance-authority';

export const cardStyles = cva(
  'rounded-xl backdrop-blur-sm transition-all',
  {
    variants: {
      variant: {
        default: 'bg-white/5 border border-white/10',
        gradient: 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10',
        outlined: 'bg-transparent border border-white/20'
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8'
      },
      hoverable: {
        true: 'hover:bg-white/[0.08] hover:border-white/20 cursor-pointer',
        false: ''
      }
    },
    defaultVariants: {
      variant: 'default',
      padding: 'md',
      hoverable: false
    }
  }
);

export const cardHeaderStyles = 'border-b border-white/10 pb-4 mb-4 flex items-center justify-between';
export const cardBodyStyles = '';
export const cardFooterStyles = 'border-t border-white/10 pt-4 mt-4';