import React from 'react';

module.exports = {
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Route: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => <a href={to}>{children}</a>,
  Navigate: jest.fn(() => null),
  useNavigate: jest.fn(() => jest.fn()),
  useLocation: jest.fn(() => ({ pathname: '/' })),
  useParams: jest.fn(() => ({})),
};