import { CatalogBuilder } from '@backstage/plugin-catalog-backend';
import { BitbucketCloudEntityProvider } from '@backstage/plugin-catalog-backend-module-bitbucket-cloud';

// import { ScaffolderEntitiesProcessor } from '@backstage/plugin-scaffolder-backend';
import { Router } from 'express';
import { PluginEnvironment } from '../types';
import { CatalogClient } from '@backstage/catalog-client';  // ✅ Add this import

export default async function createPlugin(
  env: PluginEnvironment,
): Promise<Router> {
  const builder = await CatalogBuilder.create(env);
  const bitbucketCloudProvider = BitbucketCloudEntityProvider.fromConfig(
    env.config,
    {
      auth: env.auth,
      catalogApi: new CatalogClient({ discoveryApi: env.discovery }),
      events: env.events,
      logger: env.logger,
      scheduler: env.scheduler,
    },
  );
  builder.addEntityProvider(bitbucketCloudProvider);
  const { processingEngine, router } = await builder.build();
  await processingEngine.start();
  return router;
}
