import { Logger } from 'winston';
import { Config } from '@backstage/config';
import { PluginCacheManager, TokenManager } from '@backstage/backend-common';
import { IdentityApi } from '@backstage/plugin-auth-node';
import { PermissionEvaluator } from '@backstage/plugin-permission-common';
import { EventBroker, EventsService } from '@backstage/plugin-events-node';
import { SignalsService } from '@backstage/plugin-signals-node';
import {
  UrlReaderService,
  SchedulerService,
  DatabaseService,
  DiscoveryService,
  AuthService,  // ✅ Import AuthService
} from '@backstage/backend-plugin-api';

export type PluginEnvironment = {
  logger: Logger;
  cache: PluginCacheManager;
  database: DatabaseService;
  config: Config;
  reader: UrlReaderService;
  discovery: DiscoveryService;
  tokenManager: TokenManager;
  permissions: PermissionEvaluator;
  scheduler: SchedulerService;
  identity: IdentityApi;
  auth: AuthService;  // ✅ Add this missing property
  /**
   * @deprecated use `events` instead
   */
  eventBroker: EventBroker;
  events: EventsService;
  signals: SignalsService;
};
