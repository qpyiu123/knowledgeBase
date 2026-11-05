import { Drawer, type DrawerRootProps } from '@mantine/core';
import { useViewportSize } from '@mantine/hooks';
import { useId, useRef, useState, type ReactNode } from 'react';

type Props = Pick<DrawerRootProps, 'opened' | 'onClose' | 'trapFocus' | 'lockScroll' | 'classNames'> & {
  title: ReactNode;
  defaultWidth: number;
  resizeLabel: string;
  withOverlay?: boolean;
  children: ReactNode;
};

export default function ResizableDrawer({
  opened, onClose, title, defaultWidth, resizeLabel, withOverlay = true, children, ...rootProps
}: Props) {
  const panelId = useId();
  const { width: viewport } = useViewportSize();
  const [preferredWidth, setWidth] = useState(defaultWidth);
  const drag = useRef<{ id: number; x: number; width: number } | null>(null);
  const max = viewport || window.innerWidth;
  const min = Math.min(320, max);
  const clamp = (value: number) => Math.max(min, Math.min(max, Math.round(value)));
  const width = clamp(preferredWidth);

  return (
    <Drawer.Root {...rootProps} opened={opened} onClose={onClose} position="right" size={width}>
      {withOverlay && <Drawer.Overlay />}
      <Drawer.Content id={panelId} classNames={{ content: 'resizable-drawer' }}>
        <div
          className="drawer-resizer"
          role="separator"
          tabIndex={0}
          aria-label={resizeLabel}
          aria-controls={panelId}
          aria-orientation="vertical"
          aria-valuemin={min}
          aria-valuemax={max}
          aria-valuenow={width}
          onPointerDown={(event) => {
            if (event.button !== 0 || drag.current) return;
            drag.current = { id: event.pointerId, x: event.clientX, width };
            event.currentTarget.setPointerCapture(event.pointerId);
          }}
          onPointerMove={(event) => {
            const start = drag.current;
            if (start?.id === event.pointerId) setWidth(clamp(start.width + start.x - event.clientX));
          }}
          onLostPointerCapture={() => { drag.current = null; }}
          onKeyDown={(event) => {
            const steps = { ArrowLeft: 24, ArrowRight: -24 };
            if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
              event.preventDefault();
              setWidth(clamp(width + steps[event.key]));
            }
          }}
        />
        <Drawer.Header>
          <Drawer.Title>{title}</Drawer.Title>
          <Drawer.CloseButton aria-label="关闭侧栏" />
        </Drawer.Header>
        <Drawer.Body className="resizable-drawer-body">{children}</Drawer.Body>
      </Drawer.Content>
    </Drawer.Root>
  );
}
