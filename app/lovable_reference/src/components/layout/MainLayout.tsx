import { Outlet } from 'react-router-dom';
import { AppSidebar } from './AppSidebar';

export function MainLayout() {
  return (
    <div className="min-h-screen w-full bg-background">
      <AppSidebar />
      <main className="ml-64 min-h-screen p-6">
        <Outlet />
      </main>
    </div>
  );
}
